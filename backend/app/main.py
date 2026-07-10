from __future__ import annotations

import shutil
import tempfile
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse, Response

from app.config import Settings, get_settings
from app.database import Base, make_session_factory
from app.runners.controlled import ControlledRunner
from app.services.check_service import CheckService, sha256_file
from app.services.explanation import ExplanationProvider, TemplateExplanationProvider
from app.services.extractor import ExtractionError, SafeExtractor
from app.services.reports import ReportRepository, RunNotFoundError, export_json, export_markdown
from app.services.rules import InvalidRuleError, RuleConflictError, RuleNotFoundError, RuleService


def error_response(
    status: int, code: str, message: str, request: Request, details: object = None
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message, "details": details, "request_id": request_id}},
    )


def create_app(
    settings: Settings | None = None,
    explanation_provider: ExplanationProvider | None = None,
) -> FastAPI:
    settings = settings or get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    factory = make_session_factory(settings.database_url)
    rule_service = RuleService(settings.builtin_rules_dir, settings.custom_rules_dir)
    repository = ReportRepository(factory)
    extractor = SafeExtractor(
        settings.workspace_dir,
        max_zip_bytes=settings.max_upload_bytes,
        max_files=settings.max_zip_files,
        max_extracted_bytes=settings.max_extracted_bytes,
    )
    runner = ControlledRunner(settings.allow_untrusted_execution, settings.output_limit)
    checker = CheckService(runner)
    provider = explanation_provider or TemplateExplanationProvider()

    @asynccontextmanager
    async def lifespan(_app: FastAPI):  # type: ignore[no-untyped-def]
        engine = factory.kw["bind"]
        Base.metadata.create_all(engine)
        yield
        engine.dispose()

    app = FastAPI(title="SubmitReady API", version="0.1.0", lifespan=lifespan)

    @app.middleware("http")
    async def request_id(request: Request, call_next):  # type: ignore[no-untyped-def]
        request.state.request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(422, "INVALID_REQUEST", "Request validation failed", request, exc.errors())

    @app.get("/api/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "execution_enabled": settings.allow_untrusted_execution, "sandboxed": False}

    @app.get("/api/rules")
    def list_rules(request: Request):  # type: ignore[no-untyped-def]
        try:
            return rule_service.list()
        except InvalidRuleError as exc:
            return error_response(500, "RULE_STORE_INVALID", "A stored rule is invalid", request, str(exc))

    @app.get("/api/rules/template")
    def rule_template() -> PlainTextResponse:
        return PlainTextResponse(rule_service.template(), media_type="application/yaml")

    @app.post("/api/rules", status_code=201)
    async def import_rule(request: Request, rule: UploadFile = File(...)):  # type: ignore[no-untyped-def]
        content = await rule.read(512 * 1024 + 1)
        if len(content) > 512 * 1024:
            return error_response(413, "RULE_TOO_LARGE", "Rule file exceeds 512 KiB", request)
        try:
            return rule_service.import_yaml(content)
        except InvalidRuleError as exc:
            return error_response(422, "INVALID_RULE", "Rule validation failed", request, str(exc))
        except RuleConflictError:
            return error_response(409, "RULE_CONFLICT", "Rule ID already exists", request)

    @app.post("/api/runs", status_code=201)
    async def create_run(request: Request, rule_id: str = Form(...), project: UploadFile = File(...)):  # type: ignore[no-untyped-def]
        try:
            selected_rule = rule_service.get(rule_id)
        except RuleNotFoundError:
            return error_response(404, "RULE_NOT_FOUND", "Rule was not found", request)
        if not project.filename or not project.filename.casefold().endswith(".zip"):
            return error_response(422, "INVALID_UPLOAD", "Only ZIP files are accepted", request)
        run_id = str(uuid.uuid4())
        temp_path: Path | None = None
        workspace: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip", dir=settings.data_dir) as temporary:
                temp_path = Path(temporary.name)
                total = 0
                while chunk := await project.read(64 * 1024):
                    total += len(chunk)
                    if total > settings.max_upload_bytes:
                        return error_response(413, "ZIP_TOO_LARGE", "ZIP exceeds upload limit", request)
                    temporary.write(chunk)
            project_hash = sha256_file(temp_path)
            workspace = extractor.extract(temp_path, run_id)
            report = checker.run(run_id, Path(project.filename).stem, project_hash, workspace, selected_rule)
            repository.save(report, str(workspace))
            return {
                "id": run_id,
                "status": report.status,
                "stage": "complete",
                "project_name": report.project_name,
                "project_hash": report.project_hash,
                "execution_enabled": settings.allow_untrusted_execution,
                "sandboxed": False,
            }
        except ExtractionError as exc:
            return error_response(413 if exc.code == "ZIP_TOO_LARGE" else 400, exc.code, str(exc), request)
        except Exception:
            if workspace is not None:
                shutil.rmtree(workspace, ignore_errors=True)
            return error_response(500, "INTERNAL_ERROR", "The check could not be completed", request)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

    @app.get("/api/runs")
    def list_runs():  # type: ignore[no-untyped-def]
        return repository.list()

    def lookup(run_id: str, request: Request):  # type: ignore[no-untyped-def]
        try:
            return repository.get_report(run_id)
        except RunNotFoundError:
            return error_response(404, "RUN_NOT_FOUND", "Run was not found", request)

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: str, request: Request):  # type: ignore[no-untyped-def]
        report = lookup(run_id, request)
        if isinstance(report, JSONResponse):
            return report
        return {"id": report.run_id, "status": report.status, "stage": "complete", "report": report}

    @app.get("/api/runs/{run_id}/report")
    def get_report(run_id: str, request: Request):  # type: ignore[no-untyped-def]
        return lookup(run_id, request)

    @app.get("/api/runs/{run_id}/export.json")
    def json_export(run_id: str, request: Request):  # type: ignore[no-untyped-def]
        report = lookup(run_id, request)
        if isinstance(report, JSONResponse):
            return report
        return Response(
            export_json(report),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="submitready-{run_id}.json"'},
        )

    @app.get("/api/runs/{run_id}/export.md")
    def markdown_export(run_id: str, request: Request):  # type: ignore[no-untyped-def]
        report = lookup(run_id, request)
        if isinstance(report, JSONResponse):
            return report
        return Response(
            export_markdown(report),
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="submitready-{run_id}.md"'},
        )

    @app.post("/api/runs/{run_id}/explanation")
    def explain(run_id: str, request: Request):  # type: ignore[no-untyped-def]
        report = lookup(run_id, request)
        if isinstance(report, JSONResponse):
            return report
        outputs = []
        for result in (report.build, report.test):
            if result and (result.return_code or result.timed_out):
                outputs.extend([result.stdout, result.stderr])
        if not outputs:
            outputs.extend(report.failure_reasons)
        return provider.explain("\n".join(outputs))

    @app.delete("/api/runs/{run_id}", status_code=204)
    def delete_run(run_id: str, request: Request):  # type: ignore[no-untyped-def]
        try:
            repository.delete(run_id)
            return Response(status_code=204)
        except RunNotFoundError:
            return error_response(404, "RUN_NOT_FOUND", "Run was not found", request)

    return app


app = create_app()
