from __future__ import annotations

import io
import json
import stat
import sys
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.checks.engine import CheckEngine
from app.core.redaction import redact, truncate
from app.runners.controlled import ControlledRunner, RunnerDisabledError
from app.schemas.rules import Rule
from app.services.explanation import MockExplanationProvider, TemplateExplanationProvider
from app.services.extractor import ExtractionError, SafeExtractor
from app.services.rules import RuleConflictError, RuleService


def rule_data(**updates):
    data = {
        "schema_version": 1,
        "id": "python-course-v1",
        "name": "Python Course",
        "language": "python",
        "required_files": ["main.py"],
        "forbidden_paths": [".env", ".git/**"],
        "commands": {"build": ["python", "-m", "py_compile", "main.py"]},
        "scoring": [{"id": "structure", "label": "Structure", "weight": 100}],
    }
    data.update(updates)
    return data


def make_zip(path: Path, entries: dict[str, bytes | str]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, value in entries.items():
            archive.writestr(name, value)
    return path


def test_rule_defaults_and_validation():
    rule = Rule.model_validate(rule_data())
    assert rule.limits.max_depth == 5
    assert rule.commands.timeout_seconds == 15
    with pytest.raises(ValueError):
        Rule.model_validate(rule_data(extra="no"))
    with pytest.raises(ValueError):
        Rule.model_validate(rule_data(schema_version=2))
    with pytest.raises(ValueError):
        Rule.model_validate(rule_data(required_files=["../secret"]))
    with pytest.raises(ValueError):
        Rule.model_validate(rule_data(commands={"build": ["python", "-c", "boom"]}))
    with pytest.raises(ValueError):
        Rule.model_validate(rule_data(scoring=[{"id": "x", "label": "X", "weight": 20}]))


def test_rule_service_load_import_and_conflict(tmp_path: Path):
    builtins, custom = tmp_path / "builtin", tmp_path / "custom"
    builtins.mkdir()
    (builtins / "python.yaml").write_text(
        "schema_version: 1\nid: builtin-python\nname: Builtin\nlanguage: python\n", encoding="utf-8"
    )
    service = RuleService(builtins, custom)
    assert service.list()[0].builtin is True
    custom_yaml = "schema_version: 1\nid: custom-python\nname: Custom\nlanguage: python\n"
    assert service.import_yaml(custom_yaml.encode()).rule.id == "custom-python"
    with pytest.raises(RuleConflictError):
        service.import_yaml(custom_yaml.encode())
    assert "schema_version: 1" in service.template()


@pytest.mark.parametrize("name", ["../x", "/x", "C:/x", "a/../x", "a\\..\\x", "CON/file"])
def test_extractor_rejects_unsafe_names(tmp_path: Path, name: str):
    archive = make_zip(tmp_path / "bad.zip", {name: "x"})
    extractor = SafeExtractor(tmp_path / "work")
    with pytest.raises(ExtractionError) as error:
        extractor.extract(archive, "run")
    assert error.value.code == "UNSAFE_PATH"
    assert not (tmp_path / "work" / "run").exists()


def test_extractor_valid_and_limits(tmp_path: Path):
    archive = make_zip(tmp_path / "ok.zip", {"src/main.py": "print('ok')"})
    result = SafeExtractor(tmp_path / "work").extract(archive, "run")
    assert (result / "src/main.py").read_text() == "print('ok')"
    with pytest.raises(ExtractionError) as error:
        SafeExtractor(tmp_path / "other", max_files=0).extract(archive, "run")
    assert error.value.code == "TOO_MANY_FILES"


def test_extractor_rejects_corrupt_duplicate_and_oversize(tmp_path: Path):
    broken = tmp_path / "broken.zip"
    broken.write_bytes(b"not zip")
    with pytest.raises(ExtractionError) as error:
        SafeExtractor(tmp_path / "w").extract(broken, "a")
    assert error.value.code == "INVALID_ZIP"
    big = make_zip(tmp_path / "big.zip", {"x": "12345"})
    with pytest.raises(ExtractionError) as error:
        SafeExtractor(tmp_path / "w2", max_extracted_bytes=4).extract(big, "b")
    assert error.value.code == "EXTRACTED_TOO_LARGE"


def test_extractor_rejects_duplicate_and_symlink(tmp_path: Path):
    duplicate = tmp_path / "duplicate.zip"
    with zipfile.ZipFile(duplicate, "w") as archive:
        archive.writestr("main.py", "one")
        archive.writestr("MAIN.py", "two")
    with pytest.raises(ExtractionError) as error:
        SafeExtractor(tmp_path / "w").extract(duplicate, "duplicate")
    assert error.value.code == "DUPLICATE_ZIP_ENTRY"

    link = tmp_path / "link.zip"
    info = zipfile.ZipInfo("link")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(link, "w") as archive:
        archive.writestr(info, "target")
    with pytest.raises(ExtractionError) as error:
        SafeExtractor(tmp_path / "w2").extract(link, "link")
    assert error.value.code == "UNSUPPORTED_ZIP_ENTRY"


def test_static_checks_and_sensitive_scan(tmp_path: Path):
    (tmp_path / "empty.txt").write_text("")
    (tmp_path / "debug.log").write_text("password = 'super-secret-value'")
    (tmp_path / "large.bin").write_bytes(b"x" * 20)
    rule = Rule.model_validate(
        rule_data(limits={"max_file_bytes": 10, "max_project_bytes": 100, "max_depth": 2})
    )
    items = CheckEngine().static_checks(tmp_path, rule)
    ids = {item.id: item for item in items}
    assert ids["required-files"].status == "FAIL"
    assert ids["empty-files"].status == "WARN"
    assert ids["file-sizes"].status == "FAIL"
    assert ids["temporary-files"].status == "WARN"
    assert ids["sensitive-information"].status == "FAIL"
    assert "super-secret-value" not in json.dumps([i.model_dump() for i in items])


def test_checks_are_stable_and_language_detected(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('ok')")
    rule = Rule.model_validate(rule_data())
    engine = CheckEngine()
    first = [x.model_dump() for x in engine.static_checks(tmp_path, rule)]
    second = [x.model_dump() for x in engine.static_checks(tmp_path, rule)]
    assert first == second
    assert next(x for x in first if x["id"] == "language")["status"] == "PASS"


def test_redaction_and_truncation():
    secret = "sk-" + "a" * 40
    assert secret not in redact(f"token={secret}")
    assert truncate("abcdef", 5).endswith("…")


def test_runner_disabled_output_failure_and_timeout(tmp_path: Path):
    disabled = ControlledRunner(enabled=False)
    with pytest.raises(RunnerDisabledError):
        disabled.run([sys.executable, "-c", "print(1)"], tmp_path, 1)
    runner = ControlledRunner(enabled=True, output_limit=10, validate=False)
    result = runner.run([sys.executable, "-c", "print('x'*30); raise SystemExit(3)"], tmp_path, 2)
    assert result.return_code == 3 and result.truncated
    timed = runner.run([sys.executable, "-c", "import time; time.sleep(2)"], tmp_path, 0.1)
    assert timed.timed_out


def test_runner_filters_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-secret-that-must-not-leak")
    runner = ControlledRunner(enabled=True, validate=False)
    result = runner.run([sys.executable, "-c", "import os; print(os.getenv('OPENAI_API_KEY'))"], tmp_path, 2)
    assert "fake-secret" not in result.stdout
    assert "None" in result.stdout


def test_explanation_providers():
    template = TemplateExplanationProvider().explain("pytest failed: expected 2")
    assert template.auxiliary is True and "辅助" in template.text
    mock = MockExplanationProvider("mock result")
    assert mock.explain("secret").text == "mock result"
    assert mock.calls == 1


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    builtins = tmp_path / "builtin"
    builtins.mkdir()
    (builtins / "python.yaml").write_text(
        "schema_version: 1\nid: python-course-v1\nname: Python\nlanguage: python\nrequired_files: [main.py]\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("SUBMITREADY_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("SUBMITREADY_BUILTIN_RULES_DIR", str(builtins))
    monkeypatch.setenv("SUBMITREADY_DATABASE_URL", f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    from app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client


def test_health_and_rules_api(client: TestClient):
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/api/rules").status_code == 200
    assert client.get("/api/rules/template").status_code == 200
    invalid = client.post("/api/rules", files={"rule": ("bad.yaml", b"schema_version: 2")})
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "INVALID_RULE"


def test_upload_report_export_history_delete(client: TestClient):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        archive.writestr("main.py", "print('ok')")
    response = client.post(
        "/api/runs",
        data={"rule_id": "python-course-v1"},
        files={"project": ("homework.zip", buf.getvalue(), "application/zip")},
    )
    assert response.status_code == 201, response.text
    run_id = response.json()["id"]
    assert client.get(f"/api/runs/{run_id}/report").status_code == 200
    assert (
        client.get(f"/api/runs/{run_id}/export.json").headers["content-type"].startswith("application/json")
    )
    assert "# SubmitReady" in client.get(f"/api/runs/{run_id}/export.md").text
    assert len(client.get("/api/runs").json()) == 1
    explanation = client.post(f"/api/runs/{run_id}/explanation")
    assert explanation.status_code == 200 and explanation.json()["auxiliary"] is True
    assert client.delete(f"/api/runs/{run_id}").status_code == 204
    assert client.get(f"/api/runs/{run_id}").status_code == 404


def test_upload_invalid_zip_and_missing_rule(client: TestClient):
    response = client.post(
        "/api/runs",
        data={"rule_id": "missing"},
        files={"project": ("x.zip", b"bad", "application/zip")},
    )
    assert response.status_code == 404
    response = client.post(
        "/api/runs",
        data={"rule_id": "python-course-v1"},
        files={"project": ("x.zip", b"bad", "application/zip")},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_ZIP"


def test_api_captures_build_failure_and_timeout(tmp_path: Path):
    from app.config import Settings
    from app.main import create_app

    builtins = tmp_path / "rules"
    builtins.mkdir()
    (builtins / "build.yaml").write_text(
        """schema_version: 1
id: python-build-failure
name: Build failure
language: python
required_files: [main.py]
commands:
  build: [python, -m, py_compile, main.py]
  timeout_seconds: 1
""",
        encoding="utf-8",
    )
    settings = Settings(
        data_dir=tmp_path / "data",
        builtin_rules_dir=builtins,
        database_url=f"sqlite:///{(tmp_path / 'api.db').as_posix()}",
        allow_untrusted_execution=True,
    )
    with TestClient(create_app(settings=settings)) as api:
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as archive:
            archive.writestr("main.py", "this is invalid Python !")
        response = api.post(
            "/api/runs",
            data={"rule_id": "python-build-failure"},
            files={"project": ("broken.zip", payload.getvalue(), "application/zip")},
        )
        assert response.status_code == 201
        report = api.get(f"/api/runs/{response.json()['id']}/report").json()
        assert report["status"] == "FAIL"
        assert report["build"]["return_code"] != 0
        assert next(item for item in report["checks"] if item["id"] == "test")["status"] == "SKIP"
