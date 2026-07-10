# Logical PR history

No remote pull requests are claimed by this document. It is the required local substitute when remote
repository/PR access is unavailable. Commit hashes and CI links must be added only after those actions
actually occur.

| Logical PR | Goal | Principal scope | Review focus | Verification evidence |
|---|---|---|---|---|
| 1 | Requirements and architecture | SPEC, PLAN, traceability | B-project boundary, acceptance coverage | document cold read |
| 2 | Backend foundation and rules | config, schemas, rule service | strict schema, immutable source | backend rule tests |
| 3 | Secure import and checks | extractor, static checks, scanner | fail-closed paths and limits | extractor/check tests |
| 4 | Controlled execution | runner and orchestration | no shell, timeout, env/output limits | runner tests |
| 5 | Reports and API | SQLite, exports, endpoints | error envelope, cleanup, stable history | API integration tests |
| 6 | Web interface | React routes and components | state handling, accessibility | Vitest and build |
| 7 | Distribution and examples | Docker, Compose, scripts, fixtures | reproducibility and honest sandbox boundary | script/Compose checks |
| 8 | Quality and documentation | CI and handoff docs | commands match evidence, no secrets | full local/CI gates |

Before submission, replace each generic verification cell with the real command result and attach the
actual remote PR/CI URL if one exists. A local table must not be presented as a remote review history.
