from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from app.core.redaction import safe_output
from app.schemas.report import CommandResult


class RunnerDisabledError(Exception):
    pass


class ControlledRunner:
    def __init__(self, enabled: bool = False, output_limit: int = 16 * 1024, validate: bool = True) -> None:
        self.enabled = enabled
        self.output_limit = output_limit
        self.validate = validate

    def run(self, command: list[str], cwd: Path, timeout: float) -> CommandResult:
        if not self.enabled:
            raise RunnerDisabledError("Untrusted subprocess execution is disabled")
        if self.validate:
            self._validate(command)
        env = {
            key: os.environ[key]
            for key in ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "LANG", "LC_ALL")
            if key in os.environ
        }
        env["SUBMITREADY_RUNNER"] = "controlled-subprocess"
        started = time.monotonic()
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                shell=False,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
            stdout_raw = completed.stdout.decode("utf-8", errors="replace")
            stderr_raw = completed.stderr.decode("utf-8", errors="replace")
            truncated = (
                len(stdout_raw.encode()) > self.output_limit or len(stderr_raw.encode()) > self.output_limit
            )
            return CommandResult(
                command=command,
                return_code=completed.returncode,
                stdout=safe_output(stdout_raw, self.output_limit),
                stderr=safe_output(stderr_raw, self.output_limit),
                duration_ms=int((time.monotonic() - started) * 1000),
                truncated=truncated,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = (
                (exc.stdout or b"").decode("utf-8", errors="replace")
                if isinstance(exc.stdout, bytes)
                else (exc.stdout or "")
            )
            stderr = (
                (exc.stderr or b"").decode("utf-8", errors="replace")
                if isinstance(exc.stderr, bytes)
                else (exc.stderr or "")
            )
            return CommandResult(
                command=command,
                return_code=None,
                stdout=safe_output(stdout, self.output_limit),
                stderr=safe_output(stderr, self.output_limit),
                duration_ms=int((time.monotonic() - started) * 1000),
                timed_out=True,
            )

    @staticmethod
    def _validate(command: list[str]) -> None:
        denied = {"sh", "bash", "cmd", "powershell", "pwsh", "curl", "wget", "sudo", "rm", "pip", "npm"}
        executable = Path(command[0]).name.casefold()
        if executable != command[0].casefold() or executable in denied:
            raise ValueError("Runner rejected executable")
        if any(any(char in arg for char in ";&|><\n\r\x00") for arg in command):
            raise ValueError("Runner rejected argument")
