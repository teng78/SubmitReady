from __future__ import annotations

import re
import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath


class ExtractionError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class SafeExtractor:
    def __init__(
        self,
        root: Path,
        max_zip_bytes: int = 20 * 1024 * 1024,
        max_files: int = 2_000,
        max_extracted_bytes: int = 100 * 1024 * 1024,
    ) -> None:
        self.root = root
        self.max_zip_bytes = max_zip_bytes
        self.max_files = max_files
        self.max_extracted_bytes = max_extracted_bytes

    def extract(self, archive_path: Path, run_id: object) -> Path:
        if archive_path.stat().st_size > self.max_zip_bytes:
            raise ExtractionError("ZIP_TOO_LARGE", "ZIP exceeds upload limit")
        self.root.mkdir(parents=True, exist_ok=True)
        workspace = self.root / str(run_id)
        if workspace.exists():
            raise ExtractionError("WORKSPACE_EXISTS", "Run workspace already exists")
        workspace.mkdir()
        try:
            self._extract_validated(archive_path, workspace)
            return workspace
        except ExtractionError:
            shutil.rmtree(workspace, ignore_errors=True)
            raise
        except (OSError, EOFError, RuntimeError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
            shutil.rmtree(workspace, ignore_errors=True)
            raise ExtractionError("INVALID_ZIP", "The ZIP file is damaged or unsupported") from exc

    def _extract_validated(self, archive_path: Path, workspace: Path) -> None:
        with zipfile.ZipFile(archive_path) as archive:
            entries = archive.infolist()
            if len(entries) > self.max_files:
                raise ExtractionError("TOO_MANY_FILES", "ZIP contains too many entries")
            if sum(entry.file_size for entry in entries) > self.max_extracted_bytes:
                raise ExtractionError("EXTRACTED_TOO_LARGE", "Uncompressed content exceeds limit")
            normalized: dict[str, bool] = {}
            validated: list[tuple[zipfile.ZipInfo, PurePosixPath, bool]] = []
            for entry in entries:
                path, is_dir = self._validate_entry(entry)
                key = path.as_posix().casefold()
                if key in normalized:
                    raise ExtractionError("DUPLICATE_ZIP_ENTRY", "ZIP contains duplicate paths")
                parts = path.parts
                for index in range(1, len(parts)):
                    prefix = "/".join(parts[:index]).casefold()
                    if prefix in normalized and not normalized[prefix]:
                        raise ExtractionError("DUPLICATE_ZIP_ENTRY", "File/directory path conflict")
                if not is_dir and any(existing.startswith(key + "/") for existing in normalized):
                    raise ExtractionError("DUPLICATE_ZIP_ENTRY", "File/directory path conflict")
                normalized[key] = is_dir
                validated.append((entry, path, is_dir))
            written = 0
            root = workspace.resolve()
            for entry, path, is_dir in validated:
                target = workspace.joinpath(*path.parts)
                if not target.resolve().is_relative_to(root):
                    raise ExtractionError("UNSAFE_PATH", "Entry escapes workspace")
                if is_dir:
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(entry) as source, target.open("wb") as destination:
                    while chunk := source.read(64 * 1024):
                        written += len(chunk)
                        if written > self.max_extracted_bytes:
                            raise ExtractionError("EXTRACTED_TOO_LARGE", "Uncompressed content exceeds limit")
                        destination.write(chunk)

    @staticmethod
    def _validate_entry(entry: zipfile.ZipInfo) -> tuple[PurePosixPath, bool]:
        raw = entry.filename.replace("\\", "/")
        is_dir = raw.endswith("/")
        if is_dir:
            raw = raw[:-1]
        if not raw or "\x00" in raw or raw.startswith(("/", "//")) or re.match(r"^[A-Za-z]:", raw):
            raise ExtractionError("UNSAFE_PATH", "ZIP entry has an unsafe path")
        parts = raw.split("/")
        devices = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            *(f"COM{i}" for i in range(1, 10)),
            *(f"LPT{i}" for i in range(1, 10)),
        }
        if any(
            not part
            or part in {".", ".."}
            or part.rstrip(". ") != part
            or part.split(".")[0].upper() in devices
            for part in parts
        ):
            raise ExtractionError("UNSAFE_PATH", "ZIP entry has an unsafe path")
        mode = entry.external_attr >> 16
        kind = stat.S_IFMT(mode)
        if entry.flag_bits & 0x1:
            raise ExtractionError("UNSUPPORTED_ZIP_ENTRY", "Encrypted entries are unsupported")
        if kind not in {0, stat.S_IFREG, stat.S_IFDIR}:
            raise ExtractionError("UNSUPPORTED_ZIP_ENTRY", "Links and special files are unsupported")
        return PurePosixPath(*parts), is_dir or kind == stat.S_IFDIR
