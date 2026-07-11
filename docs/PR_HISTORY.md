# Logical PR history

No remote pull requests are claimed by this document. It is the required local substitute when remote
repository/PR access is unavailable. Commit hashes and CI links must be added only after those actions
actually occur.

| Logical PR | Goal | Principal scope | Review focus | Verification evidence |
|---|---|---|---|---|
| 1 | Requirements and architecture | SPEC, PLAN, traceability | B-project boundary, acceptance coverage | `cd2cd11`, `368bc02`; independent-context cold read |
| 2 | Backend foundation through API | config, rules, extractor, checks, runner, reports | fail-closed input and deterministic results | `c3e71f2`; 21 pytest, Ruff, mypy |
| 3 | Web interface | React routes/components/API client | states and accessibility | `f81c225`; 6 Vitest, ESLint, tsc, build |
| 4 | Distribution and examples | Docker, Compose, scripts, fixtures, CI | reproducibility and honest sandbox boundary | `5a2ceb4`; 8 ZIP, YAML/CRC/security checks |
| 5 | Live contract integration | rule/report adapters and real wire mocks | cross-module API correctness | `53e32f6`; online demo + Edge/Playwright |
| 6 | Handoff documentation | README and visual overview | commands match evidence | `ad3b541` |
| 7 | Cold install repair | pnpm build allowlist | minimum lifecycle-script authority | `6087839`; second clean export passed |
| 8 | Final evidence | logs, reflection draft, acceptance | no hidden incomplete claims | final documentation commit |

No remote PR or CI URL exists in this environment. Before submission, attach actual remote PR/CI links if created. This local table must not be presented as remote review history.
