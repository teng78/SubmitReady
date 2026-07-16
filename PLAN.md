# SubmitReady 实现计划

状态标记：`[ ]` 未开始，`[~]` 进行中，`[x]` 已完成。每个实现任务遵循失败测试 → 最小实现 → 重构 → spec/质量复核。

## P0 需求与规约（依赖：无）

- [x] T00 读取通用、B、A 三份要求和仓库说明；验证：形成要求差异与限制记录。
- [x] T01 编写 `docs/SPEC.md`；验证：覆盖用户故事、模块 I/O/边界、安全、数据/API、非 Agent 边界、验收。
- [x] T02 编写本计划；验证：每项给出文件、依赖、失败测试和验收命令。
- [x] T03 独立上下文规约冷读；输入仅 SPEC/PLAN；验证：记录歧义、修订 diff。依赖 T01–T02。冷读指出规则 schema/权威源、ZIP 跨平台语义和清理职责缺口，均已修订。

## P1 后端基础（依赖：P0）

- [x] T10 建立 `backend/pyproject.toml`、配置、DB、模型和 FastAPI 骨架。验证纳入 21 个后端测试。
- [x] T11 严格规则模型与 YAML 服务；三份规则均通过实际 Pydantic 校验。
- [x] T12 安全 ZIP 导入；路径/大小/损坏/特殊项拒绝由后端测试覆盖。

## P2 检查与运行（依赖：T10–T12）

- [x] T20 静态检查已实现并测试。
- [x] T21 敏感扫描和日志脱敏已实现并测试。
- [x] T22 Runner 接口、禁用默认值、超时/截断/环境白名单已实现并测试；完整子进程树隔离未证明。
- [x] T23 编排和报告已实现；当前同步执行。

## P3 API、持久化和 AI 辅助（依赖：P2）

- [x] T30 SQLite 历史与 JSON/Markdown 导出已完成。
- [x] T31 REST API 已完成；真实在线 demo 通过。
- [x] T32 Template/Mock ExplanationProvider 已完成，无 Key 路径通过。

## P4 前端（依赖：API schema 稳定）

- [x] T40 React/TypeScript/API client/路由与 Notebook UI 完成。
- [x] T41 首页/新建/进行页完成。
- [x] T42 报告/历史/规则页完成；前端 6 tests。
- [x] T43 桌面与 390px Edge/Playwright QA 通过，控制台无错误。

## P5 分发、样例和质量（依赖：P3–P4）

- [x] T50 七类项目、八个确定性 ZIP 已生成（含 Zip Slip）。
- [x] T51 Python/PowerShell/Make 入口已提供；Python 统一入口真实通过。
- [x] T52 Dockerfile/nginx/Compose 已提供；GitHub Actions 已完成 Compose 双镜像和根目录单镜像构建，Render 已完成根目录 Dockerfile 部署。本机无 Docker，因此本机 Compose `up/down` 未执行。
- [x] T53 GitHub Actions 与 GitLab `unit-test` job 已提供。
- [x] T54 全量本地门禁通过：21 pytest + 6 Vitest，所有 lint/type/build 通过。

## P6 文档与交付（依赖：全量验证）

- [x] T60 README 与辅助文档齐全。
- [x] T61 SPEC_PROCESS、AGENT_LOG、PR_HISTORY 记录真实动作和限制。
- [x] T62 第二次全新副本冷启动通过；第一次失败及修复已记录。
- [x] T63 学生已审阅、修改并确认 2351 字最终反思稿。
- [x] T64 最终验收见 `docs/ACCEPTANCE.md`；GitHub Actions、Docker 构建和 Render WebUI 均已有远程证据。
- [x] T65 最终交付复核：独立解压交付 ZIP，逐项核对课程要求，复跑 21 个后端测试、6 个前端测试、lint、类型检查、生产构建、离线演示与凭据扫描。
- [x] T66 交付整改：根目录必交文档改为完整正文，补充分发命令、依赖许可证、提交映射、反思必答项和公开镜像工作流。

## 任务与提交映射

| 阶段 | 主要任务 | 提交 |
|---|---|---|
| P0 | T00–T03 需求、SPEC、PLAN、冷读修订 | `cd2cd11`, `368bc02` |
| P1–P3 | T10–T32 后端、检查引擎、API、报告 | `c3e71f2` |
| P4 | T40–T43 前端与交互 | `f81c225`, `53e32f6` |
| P5 | T50–T54 示例、CI、Docker、质量门禁 | `5a2ceb4`, `6087839` |
| P6 | T60–T64 文档、冷启动、验收与部署 | `ad3b541`, `791def5`, `0b7fd61`, `3ebffdf`, `bc14593`, `fd9e5cf` |
| 最终整改 | T65–T66 独立交付审计与材料完善 | `daa7634` 及最终证据提交 |

## 依赖与并行策略

`P0 → P1 → P2 → P3 → P4/P5 → P6`。规则与解压可并行；静态检查与 runner 可并行；API 稳定后前端和样例/CI 可并行。当前共享工作区不安全地支持真实并行 worktree 合并，因此采用目录所有权分工和小提交；这一偏离记录在过程文档。

## 风险控制

- 命令执行：默认关闭；测试仅运行受控假程序。
- ZIP：先验证中央目录元数据，再逐块写出并复核实际字节。
- 平台：Windows 进程终止与 POSIX 分支分别测试可达逻辑。
- 前端工具：优先使用 Codex 随附 Node/pnpm；锁定 lockfile。
- Docker 缺失：不声称本机运行；以 GitHub Actions 实际构建和 Render 部署作为远程证据。
- 课程过程工具缺失：保留清晰的等价证据和偏差说明。
