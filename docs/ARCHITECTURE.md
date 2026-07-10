# Architecture

SubmitReady is a local-first, single-instance web application. It deliberately uses deterministic
services rather than an agent loop.

```text
Browser
  | HTTP /api
  v
React SPA --served by--> nginx
                         |
                         v
                    FastAPI routes
                 /       |        \
       RuleService  CheckService  Report repository
          |          /       \          |
    versioned YAML  extractor  runner   SQLite
                       |         |
                 run workspace  validated argv
```

## Components and boundaries

- The React client handles navigation, forms, progress and report presentation. It never receives a
  server credential or a free-form shell field.
- nginx serves static assets and proxies `/api` to FastAPI. The API is the only trusted boundary from
  browser data into application services.
- Rule handling parses strict, versioned YAML. The immutable validated snapshot is the only command
  source accepted by the runner.
- Safe extraction owns ZIP limits and path validation. It writes each run into a distinct directory
  below the configured workspace root.
- The check engine owns deterministic ordering and result aggregation. Checks do not persist data or
  select their own tools.
- The controlled runner executes an argument array without a shell, with timeout, output cap and an
  environment allowlist. It is disabled by default and is not a complete sandbox.
- The report repository stores run metadata, the rule snapshot and report JSON in SQLite. Exports are
  derived from stored data.
- Explanation providers receive only a redacted, truncated error summary in one request. The default
  template provider needs no network or key.

## Deployment

Docker Compose runs separate backend and nginx containers. Persistent SQLite and workspaces use the
`submitready-data` volume. CPU, memory and process limits reduce accidental resource exhaustion; the
backend runs as UID 10001 with all Linux capabilities dropped. A root `Dockerfile` also supplies a
single-image distribution for simple demonstrations, while Compose is preferred for operation.

SQLite and local files make this a single-replica design. Horizontal scaling would require a shared
database, object storage, distributed job coordination and tenant authorization, all intentionally
outside this course scope.
