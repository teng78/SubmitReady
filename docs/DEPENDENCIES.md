# 第三方依赖与许可证

SubmitReady 自身采用 MIT License。下表列出源代码直接声明的主要依赖；精确版本以
`frontend/package.json`、`frontend/pnpm-lock.yaml` 和 `backend/pyproject.toml` 为准。

| 依赖 | 用途 | 上游许可证 |
|---|---|---|
| FastAPI | REST API | MIT |
| Pydantic / pydantic-settings | 配置和 Schema 校验 | MIT |
| SQLAlchemy | SQLite ORM | MIT |
| Uvicorn | ASGI 服务 | BSD-3-Clause |
| PyYAML | YAML 规则解析 | MIT |
| python-multipart | 上传表单解析 | Apache-2.0 |
| React / React DOM | Web UI | MIT |
| React Router | 前端路由 | MIT |
| Vite | 前端构建 | MIT |
| TypeScript | 类型检查和编译 | Apache-2.0 |
| Vitest | 前端测试 | MIT |
| Testing Library | UI 测试 | MIT |
| pytest | 后端测试 | MIT |
| Ruff | 格式与静态检查 | MIT |
| mypy | Python 类型检查 | MIT |
| nginx | 单镜像静态资源和反向代理 | BSD-2-Clause |

许可证名称用于交付审阅，不替代依赖包随附的原始许可证文本。重新分发镜像或二进制产物前，
应按锁文件中的最终依赖集合重新生成软件物料清单，并保留各上游项目的许可证与通知文件。
