from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Status = Literal["PASS", "WARN", "FAIL", "SKIP"]


class CheckItem(BaseModel):
    id: str
    label: str
    status: Status
    category: Literal["structure", "size", "hygiene", "security", "language", "build", "test", "system"]
    message: str
    suggestion: str | None = None
    details: list[str] = Field(default_factory=list)


class CommandResult(BaseModel):
    command: list[str]
    return_code: int | None
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool = False
    truncated: bool = False


class Report(BaseModel):
    run_id: str
    project_name: str
    project_hash: str
    rule_id: str
    rule_name: str
    rule_version: int
    rule_revision: str
    started_at: datetime
    finished_at: datetime
    duration_ms: int
    status: Status
    checks: list[CheckItem]
    build: CommandResult | None = None
    test: CommandResult | None = None
    failure_reasons: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    security_warnings: list[str] = Field(default_factory=list)
    environment: dict[str, str]
    rule_snapshot: dict[str, object]


class Explanation(BaseModel):
    text: str
    auxiliary: bool = True
    provider: str
