"""Fail CI when tracked production files contain likely credentials."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {
    ".git",
    "node_modules",
    ".venv",
    "dist",
    "__pycache__",
    "generated",
    "tests",
}
SKIP_PREFIXES = ("examples/projects/fake-secret/",)
PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "OpenAI-style key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}


def tracked_files() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=False
    )
    if completed.returncode:
        return [path for path in ROOT.rglob("*") if path.is_file()]
    return [ROOT / item.decode() for item in completed.stdout.split(b"\0") if item]


def main() -> int:
    failures: list[str] = []
    for path in tracked_files():
        relative = path.relative_to(ROOT).as_posix()
        if relative == ".env" or relative.endswith("/.env"):
            failures.append(f"tracked dotenv file: {relative}")
            continue
        if relative.startswith(SKIP_PREFIXES) or any(
            part in SKIP_PARTS for part in path.parts
        ):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for label, pattern in PATTERNS.items():
            if (
                pattern.search(text)
                and "FAKE" not in text
                and "example" not in relative.lower()
            ):
                failures.append(f"possible {label}: {relative}")
    if failures:
        print("Credential policy failed (values intentionally not echoed):")
        print("\n".join(f"- {item}" for item in failures))
        return 1
    print(
        "Credential policy passed; no tracked .env or high-confidence production secret found."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
