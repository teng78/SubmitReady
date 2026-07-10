# Contributing to SubmitReady

SubmitReady is a course project with deterministic, security-sensitive behavior. Keep changes small,
typed, tested, and free of credentials.

## Local checks

1. Install Python 3.11+ and Node.js 20+.
2. Run `make install` (or install `backend[dev]` and run `npm install` in `frontend`).
3. Run `python scripts/test_all.py --skip-install` before proposing a change.
4. Regenerate fixtures with `python scripts/generate_examples.py --clean` when example sources change.

Tests must be offline and must never call a real LLM. Use unmistakably fake credential values only in
test or fixture directories. Do not add arbitrary shell input to the web API. Any runner change needs
tests for validation, environment filtering, output limits, failure, and timeout.

Use focused commit messages such as `feat(rules): validate command arrays` or
`test(extractor): reject Windows device paths`. A review should check specification compliance first,
then implementation quality and security boundaries.
