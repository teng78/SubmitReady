from __future__ import annotations

import re
from pathlib import Path

from app.core.redaction import redact

_SIGNATURES = [
    ("OpenAI/API token", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("GitHub credential", re.compile(r"\b(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("Password assignment", re.compile(r"(?i)\b(?:password|passwd)\s*[:=]\s*['\"]?[^\s'\"]{8,}")),
    (
        "Cloud/API credential",
        re.compile(r"(?i)\b(?:api[_-]?key|client[_-]?secret|access[_-]?token)\s*[:=]\s*['\"]?[^\s'\"]{12,}"),
    ),
]


def scan_file(path: Path, relative: str) -> list[str]:
    if path.name == ".env":
        return [f"{relative}: environment file must not be submitted"]
    try:
        if path.stat().st_size > 2 * 1024 * 1024 or b"\x00" in path.read_bytes()[:4096]:
            return []
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    findings: list[str] = []
    for label, pattern in _SIGNATURES:
        if pattern.search(content):
            findings.append(f"{relative}: {label} pattern found")
    return [redact(item) for item in findings]
