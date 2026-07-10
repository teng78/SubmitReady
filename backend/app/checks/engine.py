from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Literal

from app.checks.secrets import scan_file
from app.schemas.report import CheckItem
from app.schemas.rules import Rule

_TEMP = {".ds_store", "thumbs.db", "desktop.ini"}
_TEMP_SUFFIXES = ("~", ".tmp", ".swp", ".log", ".pyc")
_EXTENSIONS = {"python": {".py"}, "c": {".c", ".h"}, "cpp": {".cpp", ".cc", ".cxx", ".hpp", ".h"}}


class CheckEngine:
    def static_checks(self, workspace: Path, rule: Rule) -> list[CheckItem]:
        files = self._files(workspace, rule.ignore_paths)
        paths = [relative for _, relative in files]
        required_missing = [
            pattern for pattern in rule.required_files if not any(fnmatch.fnmatch(p, pattern) for p in paths)
        ]
        forbidden = sorted(
            p for p in paths if any(fnmatch.fnmatch(p, pattern) for pattern in rule.forbidden_paths)
        )
        empty = sorted(relative for path, relative in files if path.stat().st_size == 0)
        oversized = sorted(
            relative for path, relative in files if path.stat().st_size > rule.limits.max_file_bytes
        )
        total = sum(path.stat().st_size for path, _ in files)
        deep = sorted(p for p in paths if len(Path(p).parts) > rule.limits.max_depth)
        temporary = sorted(
            p for p in paths if Path(p).name.casefold() in _TEMP or p.casefold().endswith(_TEMP_SUFFIXES)
        )
        detected = {
            language: sum(Path(p).suffix.casefold() in extensions for p in paths)
            for language, extensions in _EXTENSIONS.items()
        }
        secret_findings = (
            sorted(f for path, rel in files for f in scan_file(path, rel)) if rule.sensitive_scan else []
        )
        return [
            self._item(
                "required-files",
                "Required files",
                "structure",
                required_missing,
                True,
                "Add the missing files.",
            ),
            self._item(
                "forbidden-paths",
                "Forbidden paths",
                "structure",
                forbidden,
                True,
                "Remove forbidden content.",
            ),
            self._item(
                "directory-depth", "Directory depth", "structure", deep, True, "Flatten the archive layout."
            ),
            self._item(
                "empty-files", "Empty files", "hygiene", empty, False, "Remove or populate empty files."
            ),
            self._item("file-sizes", "File size limits", "size", oversized, True, "Reduce oversized files."),
            CheckItem(
                id="project-size",
                label="Project size",
                category="size",
                status="FAIL" if total > rule.limits.max_project_bytes else "PASS",
                message=f"Project contains {total} bytes.",
                suggestion="Remove generated or large files."
                if total > rule.limits.max_project_bytes
                else None,
            ),
            self._item(
                "temporary-files", "Temporary files", "hygiene", temporary, False, "Remove temporary files."
            ),
            CheckItem(
                id="language",
                label="Language recognition",
                category="language",
                status="PASS" if detected[rule.language] > 0 else "WARN",
                message=f"Detected counts: {detected}.",
                suggestion=None if detected[rule.language] else f"Include {rule.language} source files.",
            ),
            (
                self._item(
                    "sensitive-information",
                    "Sensitive information",
                    "security",
                    secret_findings,
                    True,
                    "Remove and rotate exposed credentials.",
                )
                if rule.sensitive_scan
                else CheckItem(
                    id="sensitive-information",
                    label="Sensitive information",
                    category="security",
                    status="SKIP",
                    message="Disabled by rule.",
                )
            ),
        ]

    @staticmethod
    def _item(
        item_id: str,
        label: str,
        category: Literal["structure", "size", "hygiene", "security", "language", "build", "test", "system"],
        details: list[str],
        fail: bool,
        suggestion: str,
    ) -> CheckItem:
        return CheckItem(
            id=item_id,
            label=label,
            category=category,
            status=("FAIL" if fail else "WARN") if details else "PASS",
            message=f"Found {len(details)} issue(s)." if details else "No issues found.",
            suggestion=suggestion if details else None,
            details=details,
        )

    @staticmethod
    def _files(workspace: Path, ignore: list[str]) -> list[tuple[Path, str]]:
        result: list[tuple[Path, str]] = []
        for path in workspace.rglob("*"):
            if path.is_file():
                relative = path.relative_to(workspace).as_posix()
                if not any(fnmatch.fnmatch(relative, pattern) for pattern in ignore):
                    result.append((path, relative))
        return sorted(result, key=lambda pair: pair[1])
