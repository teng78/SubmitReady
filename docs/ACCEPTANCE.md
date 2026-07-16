# 最终验收表

> 2026-07-16 更新：学生已确认课程无需 NJU Git；远程仓库采用公开 GitHub。

| 验收项 | 结果 | 证据/限制 |
|---|---|---|
| 30 秒说明、真实用户价值 | 通过 | README/SPEC |
| 五个职责清晰模块 | 通过 | extractor/rules/checks/runner/reports |
| UI 完整主流程 | 通过 | Edge/Playwright 上传→报告→历史，0 console error |
| 无真实 LLM 可用 | 通过 | Template/Mock Provider |
| 无自主 Agent 循环 | 通过 | 固定 CheckService 流程 |
| 安全解压 | 通过 | pytest Zip Slip/路径/特殊项/损坏/限制 |
| 严格规则校验 | 通过 | 三规则 + 非法/危险命令测试 |
| 确定性检查与敏感扫描 | 通过 | 后端测试与确定性 ZIP |
| 命令超时/输出/环境边界 | 通过（降级） | Runner 测试；subprocess 非沙箱、默认关闭 |
| 报告保存/导出/历史删除 | 通过 | API integration + online demo |
| 后端测试 | 通过 | 21 passed |
| 前端测试 | 通过 | 6 passed |
| lint/类型/构建 | 通过 | Ruff、mypy 22 files、ESLint、tsc、Vite 51 modules |
| CI 配置 | 通过 | GitHub Actions success：run 29142155058；另有 `.gitlab-ci.yml` `unit-test` |
| Docker 构建 | 通过（远程） | GitHub Actions 与 Render 构建成功；本机无 Docker CLI |
| README 命令/冷启动 | 部分通过 | 全新副本安装与 test/demo 通过；Docker 命令未本机执行 |
| 凭据安全 | 通过（当前范围） | 无外部 Key；`.env` 未跟踪；扫描通过 |
| 过程文档/反思 | 通过（有过程偏差） | 学生最终反思 2351 字；Superpowers 技能不可用的偏差已如实记录 |
| 示例与演示 | 通过 | 7 项目、8 ZIP、online demo 导出 Markdown |
| Git 小步提交 | 通过 | 10+ 语义提交已推送到公开 GitHub；无远程 PR |
| worktree/不同类型 agent | **未完成** | 共享工作区/同类 Codex，已记录偏差 |
| 公网 WebUI | 通过 | https://submitready.onrender.com；首页和 `/api/health` 外部验证 200 |
| 公共 registry 镜像 | **未完成** | Render 从源码构建，尚未发布独立公共镜像 |

结论：核心应用、学生反思、干净副本、远程 CI、Docker 构建和公网 WebUI 均已完成。课程指定的 Superpowers/worktree/不同类型智能体存在已记录的过程偏差；公共 registry 镜像和真实 PR 历史仍未提供。
