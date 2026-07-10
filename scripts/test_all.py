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
        npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
        if npm is None:
            raise SystemExit("npm was not found; install Node.js 20 or newer")
        lockfile = frontend / "package-lock.json"
        if not args.skip_install:
            run(
                "frontend dependencies",
                [npm, "ci" if lockfile.exists() else "install"],
                frontend,
            )
        run("frontend lint", [npm, "run", "lint"], frontend)
        run("frontend types", [npm, "run", "typecheck"], frontend)
        run("frontend tests", [npm, "test"], frontend)
        run("frontend build", [npm, "run", "build"], frontend)
    print("\nAll requested quality gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
