"""Run the same offline quality gates used by CI."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str], cwd: Path = ROOT) -> None:
    print(f"\n== {label} ==")
    print(" ".join(command))
    completed = subprocess.run(
        command, cwd=cwd, env={**os.environ, "PYTHONUNBUFFERED": "1"}
    )
    if completed.returncode:
        raise SystemExit(completed.returncode)


def prepare_frontend_path() -> None:
    """Expose Node, including the runtime bundled with Codex desktop."""
    if shutil.which("node"):
        return
    bundled = (
        Path.home()
        / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin"
        / ("node.exe" if os.name == "nt" else "node")
    )
    if bundled.exists():
        os.environ["PATH"] = (
            str(bundled.parent) + os.pathsep + os.environ.get("PATH", "")
        )
    if not shutil.which("node"):
        raise SystemExit("Node.js 20 or newer was not found; see README local setup")


def local_frontend_command(frontend: Path, tool: str, *args: str) -> list[str]:
    suffix = ".cmd" if os.name == "nt" else ""
    executable = frontend / "node_modules" / ".bin" / f"{tool}{suffix}"
    if not executable.exists():
        raise SystemExit(
            f"frontend dependencies are missing ({executable}); run npm install first"
        )
    return [str(executable), *args]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend-only", action="store_true")
    parser.add_argument("--frontend-only", action="store_true")
    parser.add_argument("--skip-install", action="store_true")
    args = parser.parse_args()
    if args.backend_only and args.frontend_only:
        parser.error("choose at most one component filter")

    if not args.frontend_only:
        backend = ROOT / "backend"
        run(
            "backend format",
            [sys.executable, "-m", "ruff", "format", "--check", "."],
            backend,
        )
        run("backend lint", [sys.executable, "-m", "ruff", "check", "."], backend)
        run("backend types", [sys.executable, "-m", "mypy", "app"], backend)
        run("backend tests", [sys.executable, "-m", "pytest", "-q"], backend)
        run(
            "repository credential policy", [sys.executable, "scripts/security_scan.py"]
        )

    if not args.backend_only:
        frontend = ROOT / "frontend"
        prepare_frontend_path()
        npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
        lockfile = frontend / "package-lock.json"
        if not args.skip_install and npm is not None:
            run(
                "frontend dependencies",
                [npm, "ci" if lockfile.exists() else "install"],
                frontend,
            )
        elif not (frontend / "node_modules").exists():
            raise SystemExit("npm was not found and frontend dependencies are absent")
        run(
            "frontend lint",
            local_frontend_command(frontend, "eslint", ".", "--max-warnings", "0"),
            frontend,
        )
        run(
            "frontend types",
            local_frontend_command(frontend, "tsc", "-b", "--pretty", "false"),
            frontend,
        )
        run(
            "frontend tests",
            local_frontend_command(frontend, "vitest", "run"),
            frontend,
        )
        run(
            "frontend build",
            local_frontend_command(frontend, "vite", "build"),
            frontend,
        )
    print("\nAll requested quality gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
