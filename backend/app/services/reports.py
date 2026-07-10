from __future__ import annotations

import json
import shutil

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.models import RunRecord
from app.schemas.report import Report


class RunNotFoundError(Exception):
    pass


class ReportRepository:
    def __init__(self, factory: sessionmaker[Session]) -> None:
        self.factory = factory

    def save(self, report: Report, workspace_path: str) -> None:
        record = RunRecord(
            id=report.run_id,
            project_name=report.project_name,
            project_hash=report.project_hash,
            rule_id=report.rule_id,
            rule_name=report.rule_name,
            rule_revision=report.rule_revision,
            status=report.status,
            stage="complete",
            started_at=report.started_at,
            finished_at=report.finished_at,
            duration_ms=report.duration_ms,
            workspace_path=workspace_path,
            report_json=report.model_dump_json(),
        )
        with self.factory() as session:
            session.add(record)
            session.commit()

    def list(self) -> list[dict[str, object]]:
        with self.factory() as session:
            records = session.scalars(select(RunRecord).order_by(RunRecord.started_at.desc())).all()
            return [
                {
                    "id": r.id,
                    "project_name": r.project_name,
                    "project_hash": r.project_hash,
                    "rule_id": r.rule_id,
                    "rule_name": r.rule_name,
                    "status": r.status,
                    "stage": r.stage,
                    "started_at": r.started_at,
                    "duration_ms": r.duration_ms,
                }
                for r in records
            ]

    def get_record(self, run_id: str) -> RunRecord:
        with self.factory() as session:
            record = session.get(RunRecord, run_id)
            if record is None:
                raise RunNotFoundError(run_id)
            session.expunge(record)
            return record

    def get_report(self, run_id: str) -> Report:
        return Report.model_validate_json(self.get_record(run_id).report_json)

    def delete(self, run_id: str) -> bool:
        with self.factory() as session:
            record = session.get(RunRecord, run_id)
            if record is None:
                raise RunNotFoundError(run_id)
            workspace = record.workspace_path
            session.delete(record)
            session.commit()
        try:
            shutil.rmtree(workspace)
            return True
        except FileNotFoundError:
            return True
        except OSError:
            return False


def export_markdown(report: Report) -> str:
    lines = [
        "# SubmitReady 检查报告",
        "",
        f"- 运行 ID：`{report.run_id}`",
        f"- 项目：{report.project_name}",
        f"- 规则：{report.rule_name} (`{report.rule_id}` v{report.rule_version})",
        f"- 总状态：**{report.status}**",
        f"- 耗时：{report.duration_ms} ms",
        "",
        "## 检查项",
        "",
    ]
    for item in report.checks:
        lines.append(f"- **{item.status}** {item.label}：{item.message}")
        if item.suggestion:
            lines.append(f"  - 建议：{item.suggestion}")
    if report.build:
        lines.extend(["", "## 构建输出", "", "```text", report.build.stdout + report.build.stderr, "```"])
    if report.test:
        lines.extend(["", "## 测试输出", "", "```text", report.test.stdout + report.test.stderr, "```"])
    return "\n".join(lines) + "\n"


def export_json(report: Report) -> str:
    return json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2)
