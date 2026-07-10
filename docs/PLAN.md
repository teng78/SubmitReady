# SubmitReady 实现计划

状态标记：`[ ]` 未开始，`[~]` 进行中，`[x]` 已完成。每个实现任务遵循失败测试 → 最小实现 → 重构 → spec/质量复核。

## P0 需求与规约（依赖：无）

- [x] T00 读取通用、B、A 三份要求和仓库说明；验证：形成要求差异与限制记录。
- [x] T01 编写 `docs/SPEC.md`；验证：覆盖用户故事、模块 I/O/边界、安全、数据/API、非 Agent 边界、验收。
- [x] T02 编写本计划；验证：每项给出文件、依赖、失败测试和验收命令。
- [x] T03 独立上下文规约冷读；输入仅 SPEC/PLAN；验证：记录歧义、修订 diff。依赖 T01–T02。冷读指出规则 schema/权威源、ZIP 跨平台语义和清理职责缺口，均已修订。

## P1 后端基础（依赖：P0）

- [ ] T10 建立 `backend/pyproject.toml`、配置、DB、模型和 FastAPI 骨架。红测：health/DB 临时实例；绿测：`pytest`。文件：`backend/app/{main,config,database,models}.py`。
- [ ] T11 严格规则模型与 YAML 服务（依赖 T10 配置）。红测：三份合法规则、未知字段/危险命令/版本错误；绿测：schema/template/list/import。文件：`schemas/rules.py`, `services/rules.py`, `tests/test_rules.py`, `examples/rules/*`。验收：`pytest tests/test_rules.py -q`。三份规则资产归 T11，T50 只生成项目 ZIP。
- [ ] T12 安全 ZIP 导入（依赖 T10 配置，不依赖 DB/API）。红测：Zip Slip、绝对/UNC/盘符/混合路径、链接/特殊项、重复冲突、加密/损坏包、数量/大小边界；绿测：独立目录与失败清理。文件：`services/extractor.py`, `tests/test_extractor.py`。验收：`pytest tests/test_extractor.py -q`。

## P2 检查与运行（依赖：T10–T12）

- [ ] T20 静态检查。红测：必需/禁止/空/大小/临时/层级/语言；绿测：确定性排序和状态。文件：`checks/*`, `tests/test_checks.py`。
- [ ] T21 敏感扫描和日志脱敏。红测：虚假 GitHub/OpenAI/云 Key、私钥、`.env`、密码与假阳性边界；绿测：证据不回显 secret。文件：`checks/secrets.py`, `core/redaction.py`。
- [ ] T22 Runner 接口与受控 subprocess。红测：denylist、环境过滤、输出截断、失败、超时；绿测：无 shell、进程树终止、审计结果。文件：`runners/*`, `tests/test_runner.py`。
- [ ] T23 编排和报告。红测：阶段顺序、汇总、SKIP、建议、稳定结果；绿测：CheckService。文件：`services/check_service.py`, `schemas/report.py`。

## P3 API、持久化和 AI 辅助（依赖：P2）

- [ ] T30 历史仓储与导出。红测：重复提交、列表/详情/删除、JSON/MD 内容；绿测：SQLite repository/exporter。
- [ ] T31 REST API。红测：上传→报告→导出→删除、非法 ZIP/规则/超限、统一错误；绿测：路由和异常处理。
- [ ] T32 ExplanationProvider。红测：Mock 注入、无 Key、脱敏/截断、一次调用；绿测：模板解释 endpoint。

## P4 前端（依赖：API schema 稳定）

- [ ] T40 Vite/React/TypeScript 基础、API client、路由与 Notebook token。红测：导航、错误边界；绿测：响应式 shell。
- [ ] T41 首页/新建/进行页。红测：规则选择、文件大小、加载、防重、错误；绿测：创建并轮询/导航。
- [ ] T42 报告/历史/规则页。红测：报告统计、长日志折叠、导出、历史空/删除、规则导入错误；绿测：完整交互。
- [ ] T43 可访问性与小屏 QA；验证：labels、focus、keyboard、CSS mobile、无无意义动画。

## P5 分发、样例和质量（依赖：P3–P4）

- [ ] T50 六类示例项目及 ZIP 生成脚本（规则资产在 T11）；验证：fixture 清单与 `python scripts/generate_examples.py` 幂等。
- [ ] T51 跨平台测试/演示脚本、Makefile；验证：PowerShell 与 Python 入口均传播失败码。
- [ ] T52 backend/frontend Dockerfile、nginx、Compose；验证：配置静态检查；有 Docker 环境时 build/up/health/down。
- [ ] T53 GitHub Actions 和课程要求 `.gitlab-ci.yml` `unit-test` job；验证：YAML/命令与本地一致。
- [ ] T54 全量门禁：Ruff format/check、mypy、pytest、ESLint、tsc、Vitest、Vite build、安全扫描。

## P6 文档与交付（依赖：全量验证）

- [ ] T60 README、ARCHITECTURE、SECURITY、API、DEMO、TROUBLESHOOTING、CONTRIBUTING、LICENSE。
- [ ] T61 SPEC_PROCESS、AGENT_LOG、PR_HISTORY；只能记录真实动作、结果和限制。
- [ ] T62 冷启动模拟，修复后写 `COLD_START_REPORT.md`。
- [ ] T63 `REFLECTION.md` 提供批判性草稿并醒目标注须由学生本人核验/改写（课程禁止 AI 代写）。
- [ ] T64 最终逐项验收，记录命令、数量、失败和环境阻塞。

## 依赖与并行策略

`P0 → P1 → P2 → P3 → P4/P5 → P6`。规则与解压可并行；静态检查与 runner 可并行；API 稳定后前端和样例/CI 可并行。当前共享工作区不安全地支持真实并行 worktree 合并，因此采用目录所有权分工和小提交；这一偏离记录在过程文档。

## 风险控制

- 命令执行：默认关闭；测试仅运行受控假程序。
- ZIP：先验证中央目录元数据，再逐块写出并复核实际字节。
- 平台：Windows 进程终止与 POSIX 分支分别测试可达逻辑。
- 前端工具：优先使用 Codex 随附 Node/pnpm；锁定 lockfile。
- Docker 缺失：不能伪造构建通过；提供 CI build 并在冷启动报告标阻塞。
- 课程过程工具缺失：保留清晰的等价证据和偏差说明。
