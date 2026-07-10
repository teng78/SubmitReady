# 3–5 minute demonstration

## Prepare

```bash
python scripts/generate_examples.py --clean
docker compose up --build
```

Open `http://localhost:8080`. No account or API key is required.

## Main path

1. On **New check**, select **Python Course Assignment**.
2. Upload `examples/generated/python-pass.zip` and start the check.
3. Point out the stage indicator and the warning that local execution is disabled by default.
4. Open the report and show status counts, deterministic checks and folded build/test output.
5. Export both JSON and Markdown.
6. Open **History**, locate the run, then demonstrate detail and delete actions.
7. Open **Rules** to show C, C++ and Python built-ins and the downloadable template.

For a failure path, upload `missing-required.zip`, `c-compile-error.zip`,
`python-test-fail.zip` or `fake-secret.zip` with the matching rule. Uploading `zip-slip.zip` must return
a safe-path error and must not create `escaped.txt` outside the run workspace.

With the application already running, the repeatable API route is:

```bash
python scripts/demo.py --base-url http://localhost:8080
```

It creates a Python run, waits for completion and writes the downloaded Markdown to
`examples/generated/demo-report.md`. Stop and clean up with `docker compose down --remove-orphans`.
