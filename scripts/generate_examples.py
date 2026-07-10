"""Build deterministic demo ZIP files from the readable example projects."""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "examples" / "projects"
GENERATED = ROOT / "examples" / "generated"


def _write_tree(archive: zipfile.ZipFile, source: Path) -> None:
    for path in sorted(source.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_file():
            info = zipfile.ZipInfo(path.relative_to(source).as_posix())
            info.date_time = (2020, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def _write_bytes(archive: zipfile.ZipFile, name: str, content: bytes) -> None:
    info = zipfile.ZipInfo(name)
    info.date_time = (2020, 1, 1, 0, 0, 0)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, content)


def generate(clean: bool = False) -> list[Path]:
    if clean and GENERATED.exists():
        shutil.rmtree(GENERATED)
    GENERATED.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for source in sorted(PROJECTS.iterdir(), key=lambda item: item.name):
        if not source.is_dir():
            continue
        destination = GENERATED / f"{source.name}.zip"
        with zipfile.ZipFile(destination, "w") as archive:
            _write_tree(archive, source)
        created.append(destination)

    malicious = GENERATED / "zip-slip.zip"
    with zipfile.ZipFile(malicious, "w", zipfile.ZIP_DEFLATED) as archive:
        _write_bytes(archive, "../escaped.txt", b"This file must never be extracted.")
        _write_bytes(archive, "main.py", b"print('unreachable fixture')\n")
    created.append(malicious)
    return created


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true", help="replace generated ZIPs")
    args = parser.parse_args()
    created = generate(clean=args.clean)
    for path in created:
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
