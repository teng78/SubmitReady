"""Generate fixtures and optionally execute the HTTP demonstration path."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from generate_examples import ROOT, generate


def request(
    url: str, *, data: bytes | None = None, headers: dict[str, str] | None = None
) -> bytes:
    with urllib.request.urlopen(
        urllib.request.Request(url, data=data, headers=headers or {}), timeout=30
    ) as response:
        return response.read()


def multipart(project: Path, rule_id: str) -> tuple[bytes, str]:
    boundary = f"submitready-{uuid.uuid4().hex}"
    chunks = [
        f'--{boundary}\r\nContent-Disposition: form-data; name="rule_id"\r\n\r\n{rule_id}\r\n'.encode(),
        (
            f'--{boundary}\r\nContent-Disposition: form-data; name="project"; '
            f'filename="{project.name}"\r\nContent-Type: application/zip\r\n\r\n'
        ).encode(),
        project.read_bytes(),
        f"\r\n--{boundary}--\r\n".encode(),
    ]
    return b"".join(chunks), boundary


def online_demo(base_url: str) -> Path:
    base = base_url.rstrip("/")
    health = json.loads(request(f"{base}/api/health"))
    print(f"API health: {health}")
    project = ROOT / "examples" / "generated" / "python-pass.zip"
    body, boundary = multipart(project, "python-course-v1")
    created = json.loads(
        request(
            f"{base}/api/runs",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
    )
    run_id = created.get("id") or created.get("run_id")
    if not run_id:
        raise RuntimeError(f"create response has no run id: {created}")
    for _ in range(60):
        current = json.loads(request(f"{base}/api/runs/{run_id}"))
        if str(current.get("status", "")).upper() not in {
            "PENDING",
            "RUNNING",
            "QUEUED",
        }:
            break
        time.sleep(0.5)
    else:
        raise TimeoutError("run did not complete within 30 seconds")
    markdown = request(f"{base}/api/runs/{run_id}/export.md")
    output = ROOT / "examples" / "generated" / "demo-report.md"
    output.write_bytes(markdown)
    print(f"Run {run_id} completed; Markdown export: {output.relative_to(ROOT)}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url", help="running application URL, for example http://localhost:8080"
    )
    args = parser.parse_args()
    created = generate(clean=True)
    print(f"Generated {len(created)} deterministic ZIP fixtures.")
    if args.base_url:
        try:
            online_demo(args.base_url)
        except (OSError, urllib.error.HTTPError, ValueError, RuntimeError) as exc:
            print(f"Demo failed: {exc}", file=sys.stderr)
            return 1
    else:
        print(
            "Start the app, then add --base-url http://localhost:8080 for the full API demo."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
