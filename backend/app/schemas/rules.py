from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Limits(StrictModel):
    max_file_bytes: int = Field(default=1_048_576, ge=1, le=104_857_600)
    max_project_bytes: int = Field(default=10_485_760, ge=1, le=104_857_600)
    max_depth: int = Field(default=5, ge=1, le=20)

    @model_validator(mode="after")
    def project_not_smaller(self) -> Limits:
        if self.max_project_bytes < self.max_file_bytes:
            raise ValueError("max_project_bytes must be at least max_file_bytes")
        return self


class Commands(StrictModel):
    build: list[str] | None = None
    test: list[str] | None = None
    timeout_seconds: int = Field(default=15, ge=1, le=120)
    network_disabled: bool = True


class ScoringItem(StrictModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,63}$")
    label: str = Field(min_length=1, max_length=100)
    weight: int = Field(ge=0, le=100)


class Rule(StrictModel):
    schema_version: Literal[1]
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{2,63}$")
    name: str = Field(min_length=1, max_length=100)
    language: Literal["python", "c", "cpp"]
    required_files: list[str] = Field(default_factory=list, max_length=100)
    forbidden_paths: list[str] = Field(default_factory=list, max_length=100)
    ignore_paths: list[str] = Field(default_factory=list, max_length=100)
    limits: Limits = Field(default_factory=Limits)
    commands: Commands = Field(default_factory=Commands)
    sensitive_scan: bool = True
    scoring: list[ScoringItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_contract(self) -> Rule:
        for pattern in self.required_files + self.forbidden_paths + self.ignore_paths:
            _validate_glob(pattern)
        if self.scoring:
            ids = [item.id for item in self.scoring]
            if len(ids) != len(set(ids)) or sum(item.weight for item in self.scoring) != 100:
                raise ValueError("scoring ids must be unique and weights must total 100")
        for command in (self.commands.build, self.commands.test):
            if command is not None:
                _validate_command(command, self.language)
        return self


def _validate_glob(value: str) -> None:
    if not value or "\\" in value or "\x00" in value or value.startswith("/"):
        raise ValueError(f"unsafe path pattern: {value!r}")
    if re.match(r"^[A-Za-z]:", value) or ".." in value.split("/"):
        raise ValueError(f"unsafe path pattern: {value!r}")


_ALLOWED = {
    "python": {"python", "python3", "py", "pytest"},
    "c": {"gcc", "clang", "make", "cmake", "ctest", "ninja"},
    "cpp": {"g++", "clang++", "make", "cmake", "ctest", "ninja"},
}
_DENIED = {"sh", "bash", "cmd", "powershell", "pwsh", "curl", "wget", "sudo", "rm", "pip", "npm"}


def _validate_command(command: list[str], language: str) -> None:
    if not 1 <= len(command) <= 32 or any(not isinstance(arg, str) or not arg for arg in command):
        raise ValueError("command must contain 1..32 non-empty arguments")
    executable = command[0].casefold()
    if (
        "/" in executable
        or "\\" in executable
        or executable in _DENIED
        or executable not in _ALLOWED[language]
    ):
        raise ValueError("command executable is not allowed")
    for arg in command:
        if any(char in arg for char in ";&|><\n\r\x00") or "://" in arg:
            raise ValueError("unsafe command argument")
        if arg.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", arg) or ".." in arg.split("/"):
            raise ValueError("unsafe command path")
    if executable in {"python", "python3", "py"}:
        if "-c" in command or "--command" in command:
            raise ValueError("inline Python is forbidden")
        if "-m" in command:
            index = command.index("-m")
            if index + 1 >= len(command) or command[index + 1] not in {"py_compile", "pytest", "unittest"}:
                raise ValueError("Python module is not allowed")


class RuleView(BaseModel):
    rule: Rule
    revision: str
    builtin: bool
