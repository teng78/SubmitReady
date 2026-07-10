# HTTP API

Interactive OpenAPI documentation is available at `http://localhost:8000/docs` during backend-only
development and through the deployed API path when exposed by the chosen proxy configuration.

All failures use this envelope:

```json
{"error":{"code":"UNSAFE_PATH","message":"Archive path is unsafe","details":{},"request_id":"..."}}
```

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Liveness and version information |
| GET | `/api/rules` | List built-in and imported rules |
| POST | `/api/rules` | Upload and strictly validate a YAML rule |
| GET | `/api/rules/template` | Download a schema-version-1 template |
| POST | `/api/runs` | Multipart upload (`project`, `rule_id`) and create a run |
| GET | `/api/runs` | List history, newest first |
| GET | `/api/runs/{id}` | Get run stage/status metadata |
| DELETE | `/api/runs/{id}` | Delete history and attempt workspace cleanup |
| GET | `/api/runs/{id}/report` | Get the structured report |
| GET | `/api/runs/{id}/export.json` | Download JSON report |
| GET | `/api/runs/{id}/export.md` | Download Markdown report |
| POST | `/api/runs/{id}/explanation` | Request one auxiliary explanation |

The upload must be a ZIP and defaults to a 20 MiB request limit. Rule commands cannot be supplied in
the run request; only an already validated `rule_id` is accepted. IDs are UUIDs. A repeated ZIP creates
a new ID while retaining its content hash for comparison.

Expected status codes: 200 for reads/exports, 201 or 202 for creation, 204 for deletion, 400 for invalid
ZIP, 404 for missing resources, 409 for conflicting rule IDs/run state, 413 for request limits, 422 for
schema validation, and 500 for a redacted internal error.
