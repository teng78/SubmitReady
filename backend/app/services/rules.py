from __future__ import annotations

import hashlib
from pathlib import Path

import yaml
from pydantic import ValidationError

from app.schemas.rules import Rule, RuleView


class RuleNotFoundError(Exception):
    pass


class RuleConflictError(Exception):
    pass


class InvalidRuleError(Exception):
    pass


class RuleService:
    def __init__(self, builtin_dir: Path, custom_dir: Path) -> None:
        self.builtin_dir = builtin_dir
        self.custom_dir = custom_dir
        self.custom_dir.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[RuleView]:
        values: list[RuleView] = []
        for builtin, directory in ((True, self.builtin_dir), (False, self.custom_dir)):
            if directory.exists():
                for path in sorted(directory.glob("*.yaml")):
                    values.append(self._load(path, builtin))
        return sorted(values, key=lambda item: item.rule.id)

    def get(self, rule_id: str) -> RuleView:
        for item in self.list():
            if item.rule.id == rule_id:
                return item
        raise RuleNotFoundError(rule_id)

    def import_yaml(self, content: bytes) -> RuleView:
        try:
            text = content.decode("utf-8")
            parsed = yaml.safe_load(text)
            if not isinstance(parsed, dict):
                raise ValueError("root must be an object")
            rule = Rule.model_validate(parsed)
        except (UnicodeDecodeError, yaml.YAMLError, ValidationError, ValueError) as exc:
            raise InvalidRuleError(str(exc)) from exc
        try:
            self.get(rule.id)
        except RuleNotFoundError:
            pass
        else:
            raise RuleConflictError(rule.id)
        canonical = yaml.safe_dump(
            rule.model_dump(mode="json", exclude_defaults=False), sort_keys=False, allow_unicode=True
        )
        path = self.custom_dir / f"{rule.id}.yaml"
        path.write_text(canonical, encoding="utf-8")
        return self._load(path, False)

    def _load(self, path: Path, builtin: bool) -> RuleView:
        content = path.read_bytes()
        try:
            data = yaml.safe_load(content.decode("utf-8"))
            rule = Rule.model_validate(data)
        except (UnicodeDecodeError, yaml.YAMLError, ValidationError, ValueError) as exc:
            raise InvalidRuleError(f"{path.name}: {exc}") from exc
        return RuleView(rule=rule, revision=hashlib.sha256(content).hexdigest(), builtin=builtin)

    @staticmethod
    def template() -> str:
        return """schema_version: 1
id: python-course-v1
name: Python Course
language: python
required_files: [main.py]
forbidden_paths: [.env, .git/**]
ignore_paths: [.venv/**, __pycache__/**]
limits:
  max_file_bytes: 1048576
  max_project_bytes: 10485760
  max_depth: 5
commands:
  build: [python, -m, py_compile, main.py]
  test: [python, -m, pytest, -q]
  timeout_seconds: 15
  network_disabled: true
sensitive_scan: true
scoring:
  - id: structure
    label: Required structure
    weight: 100
"""
