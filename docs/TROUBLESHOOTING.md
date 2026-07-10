# Troubleshooting

## The frontend opens but API calls fail

Run `docker compose ps` and inspect `docker compose logs backend`. The backend health endpoint is
`http://localhost:8080/api/health`. Port 8080 must be free. Do not paste logs containing private student
code or credential-like values into public issues.

## Built-in rules are missing

Run from the repository root. The application expects `examples/rules` to be present. For containers,
rebuild after changing a rule: `docker compose up --build`.

## A build/test check is skipped

This is expected while `SUBMITREADY_ALLOW_UNTRUSTED_EXECUTION=false`, the safe default. If the uploaded
project is yours and you accept the subprocess limitations in `docs/SECURITY.md`, enable it in a local
`.env` and restart. Do not enable it on a public unauthenticated deployment.

## Docker cannot write SQLite or workspaces

The image runs as UID 10001. Prefer the named Compose volume. With a host bind mount, grant that UID
write access to the target directory. `docker compose down -v` deletes local SubmitReady volume data;
use it only when loss of history is intended.

## Python/Node checks are not found

Use Python 3.11+ and Node.js 20+. Install development dependencies with `make install`, then run
`python scripts/test_all.py --skip-install`. On Windows, use `./scripts/test-all.ps1` when Make is not
installed.

## Example ZIPs are absent

They are generated artifacts and intentionally ignored by Git. Run
`python scripts/generate_examples.py --clean` or `make demo`.
