from __future__ import annotations

import re

_PATTERNS = [
    re.compile(r"\b(?:sk|ghp|github_pat)-?[A-Za-z0-9_\-]{20,}\b", re.I),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)(password|passwd|api[_-]?key|secret|token)\s*[:=]\s*['\"]?[^\s'\"]{6,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def redact(value: str) -> str:
    result = value
    for pattern in _PATTERNS:
        result = pattern.sub("[REDACTED]", result)
    return result


def truncate(value: str, limit: int = 16 * 1024) -> str:
    if len(value.encode("utf-8")) <= limit:
        return value
    encoded = value.encode("utf-8")[: max(0, limit - 3)]
    return encoded.decode("utf-8", errors="ignore") + "…"


def safe_output(value: str, limit: int = 16 * 1024) -> str:
    return truncate(redact(value), limit)
