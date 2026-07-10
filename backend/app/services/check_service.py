from __future__ import annotations

import hashlib
import platform
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from app.checks.engine import CheckEngine
from app.runners.controlled import ControlledRunner, RunnerDisabledError
from app.schemas.report import CheckItem, CommandResult, Report
from app.schemas.rules import RuleView


class CheckService:
    def __init__(self, runner: ControlledRunner) -> None:
        self.runner = runner
        self.engine = CheckEngine()

    def run(
        self, run_id: str, project_name: str, project_hash: str, workspace: Path, rule_view: RuleView
    ) -> Report:
        started = datetime.now(UTC)
        clock = time.monotonic()
        rule = rule_view.rule
        checks = self.engine.static_checks(workspace, rule)
        build_result, build_item = self._run_command(
            "build", rule.commands.build, workspace, rule.commands.timeout_seconds
        )
        checks.append(build_item)
        if build_item.status == "FAIL":
            test_result = None
            checks.append(
                CheckItem(
                    id="test",
                    label="Tests",
                    category="test",
                    status="SKIP",
                    message="Skipped because build failed.",
                )
            )
        else:
            test_result, test_item = self._run_command(
                "test", rule.commands.test, workspace, rule.commands.timeout_seconds
            )
            checks.append(test_item)
        finished = datetime.now(UTC)
        status: Literal["PASS", "WARN", "FAIL", "SKIP"] = (
            "FAIL"
            if any(c.status == "FAIL" for c in checks)
            else "WARN"
            if any(c.status == "WARN" for c in checks)
            else "PASS"
        )
        failures = [c.message for c in checks if c.status == "FAIL"]
        suggestions = [c.suggestion for c in checks if c.suggestion]
        warnings = [
            detail for c in checks if c.category == "security" and c.status != "PASS" for detail in c.details
        ]
        return Report(
            run_id=run_id,
            project_name=project_name,
            project_hash=project_hash,
            rule_id=rule.id,
            rule_name=rule.name,
            rule_version=rule.schema_version,
            rule_revision=rule_view.revision,
            started_at=started,
            finished_at=finished,
            duration_ms=int((time.monotonic() - clock) * 1000),
            status=status,
            checks=checks,
            build=build_result,
            test=test_result,
            failure_reasons=failures,
            suggestions=suggestions,
            security_warnings=warnings,
            environment={
                "platform": platform.system(),
                "python": platform.python_version(),
                "runner": "controlled-subprocess" if self.runner.enabled else "disabled",
            },
            rule_snapshot=rule.model_dump(mode="json"),
        )

    def _run_command(
        self, kind: str, command: list[str] | None, workspace: Path, timeout: int
    ) -> tuple[CommandResult | None, CheckItem]:
        category: Literal["build", "test"] = "build" if kind == "build" else "test"
        label = "Build" if kind == "build" else "Tests"
        if command is None:
            return None, CheckItem(
                id=kind, label=label, category=category, status="SKIP", message="No command configured."
            )
        try:
            result = self.runner.run(command, workspace, timeout)
        except RunnerDisabledError:
            return None, CheckItem(
                id=kind,
                label=label,
                category=category,
                status="SKIP",
                message="Untrusted execution is disabled; subprocess mode is not a complete sandbox.",
            )
        failed = result.timed_out or result.return_code != 0
        return result, CheckItem(
            id=kind,
            label=label,
            category=category,
            status="FAIL" if failed else "PASS",
            message=(
                "Command timed out."
                if result.timed_out
                else f"Command exited with code {result.return_code}."
            ),
            suggestion="Review the captured output and fix the first error." if failed else None,
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(64 * 1024):
            digest.update(chunk)
    return digest.hexdigest()
