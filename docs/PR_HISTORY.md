# Commit and logical review history

公开仓库为 <https://github.com/teng78/SubmitReady>，主分支 CI 记录见
<https://github.com/teng78/SubmitReady/actions>。本项目开发期间没有创建远程 Pull Request；
下表只记录基于小提交进行的逻辑审查阶段，不冒充远程 PR/MR。

| Logical PR | Goal | Principal scope | Review focus | Verification evidence |
|---|---|---|---|---|
| 1 | Requirements and architecture | SPEC, PLAN, traceability | B-project boundary, acceptance coverage | `cd2cd11`, `368bc02`; independent-context cold read |
| 2 | Backend foundation through API | config, rules, extractor, checks, runner, reports | fail-closed input and deterministic results | `c3e71f2`; 21 pytest, Ruff, mypy |
| 3 | Web interface | React routes/components/API client | states and accessibility | `f81c225`; 6 Vitest, ESLint, tsc, build |
| 4 | Distribution and examples | Docker, Compose, scripts, fixtures, CI | reproducibility and honest sandbox boundary | `5a2ceb4`; 8 ZIP, YAML/CRC/security checks |
| 5 | Live contract integration | rule/report adapters and real wire mocks | cross-module API correctness | `53e32f6`; online demo + Edge/Playwright |
| 6 | Handoff documentation | README and visual overview | commands match evidence | `ad3b541` |
| 7 | Cold install repair | pnpm build allowlist | minimum lifecycle-script authority | `6087839`; second clean export passed |
| 8 | Final evidence and deployment | logs, reflection, acceptance, Render | no hidden incomplete claims | `791def5` through `fd9e5cf`; [successful CI](https://github.com/teng78/SubmitReady/actions/runs/29145673577) |

限制：远程仓库有完整线性 commit 历史和成功 CI，但没有真实 PR 审查记录；课程已确认无需 NJU Git，本表仍不把逻辑阶段描述成真实 PR。
