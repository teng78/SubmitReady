# SubmitReady 产品与工程规格

状态：v1.0（2026-07-11，实施基线）  
项目方向：B · 非 Harness 应用类项目

## 1. 问题与价值

学生经常因为压缩包层级、漏交文件、编译/测试失败、临时文件或凭据泄漏等提交前问题失分。助教也缺少可复用、可审计的统一检查规则。SubmitReady 接受 ZIP 作业和版本化规则，按固定顺序执行确定性检查，并生成持久化、可导出的报告。

30 秒说明：上传作业 ZIP，选择课程规则，一次得到结构、代码、构建、测试和敏感信息检查结果；在真正提交前修掉会丢分的问题。

目标用户：高校学生、课程助教/教师、需要标准化提交自检的小型团队。

## 2. 范围与非目标

核心范围包括安全 ZIP 导入、版本化 YAML 规则、确定性检查、可控命令执行、SQLite 历史和 Web 报告。可选 AI 仅有一次性解释接口；默认模板实现，不访问网络。

非目标：在线评测/OJ、容器编排平台、代码自动修改、LLM 自主决策、工具自主选择、自我循环、恶意代码的绝对安全沙箱、用户账号与多租户权限。

## 3. 用户故事

1. 作为学生，我希望上传 ZIP 并选择教师规则，以便在提交前发现确定性问题。
2. 作为学生，我希望看到每项检查的状态、证据和建议，以便快速修复。
3. 作为学生，我希望导出 JSON/Markdown，以便保存或发给助教。
4. 作为助教，我希望导入严格校验的 YAML 规则，以便统一班级检查标准。
5. 作为助教，我希望浏览并删除历史记录，以便区分重复提交并管理本机数据。
6. 作为安全敏感用户，我希望损坏包、路径穿越和疑似凭据默认被拒绝或报告。
7. 作为无 API Key 用户，我希望所有核心检查仍可用，并得到模板化解释。
8. 作为演示者，我希望用内置样例在 3–5 分钟内完成端到端流程。

## 4. 功能规约

### 4.1 安全导入

输入为 `.zip`。上传大小默认 20 MiB；成员不超过 2,000 个；解压总量不超过 100 MiB。逐项拒绝绝对路径、盘符路径、`..` 穿越、符号链接和目标目录外路径。每次运行使用 UUID 工作目录。损坏 ZIP 返回稳定错误码。删除历史时清理工作目录；请求失败也清理临时上传。演示夹具含合法 ZIP 与 Zip Slip ZIP。

### 4.2 规则

YAML Schema 版本固定为 `1`。字段：名称、语言、必需/禁止/忽略 glob、单文件和项目大小、构建/测试参数数组、超时、网络策略、敏感扫描和评分项。未知字段拒绝，危险可执行文件和危险参数组合在导入时拒绝。内置 C/C++/Python 三份规则不可被上传覆盖；自定义规则写入应用数据目录并可下载模板。

### 4.3 检查引擎

固定阶段：清单 → 大小/空文件/临时文件 → 语言 → 敏感信息 → 构建 → 测试 → 汇总。状态为 PASS/WARN/FAIL/SKIP；分类为 structure/size/hygiene/security/language/build/test/system。忽略路径在扫描前统一过滤。输出按 UTF-8 替换解码并限制为 16 KiB。相同目录和规则在外部工具不变时得到相同项目检查项；时间、UUID、耗时除外。

### 4.4 命令运行

规则只接受参数数组，不启用 shell。可执行文件白名单按规则语言限制；拒绝 shell、包管理下载器、网络工具、提权、删除工具和解释器内联执行参数。环境仅传递 PATH、SYSTEMROOT、WINDIR、TEMP/TMP、LANG/LC_ALL 与 SubmitReady 标识，不传递 API Key。subprocess 降级模式默认关闭（`ALLOW_UNTRUSTED_EXECUTION=false`）；开启时 UI/API 明示“不是完整沙箱”。接口保留 DockerRunner；本版本提供配置验证和 Compose 资源边界，但应用内 Docker runner 仍为已知限制。

### 4.5 报告与历史

SQLite 保存运行元数据、规则快照和结构化报告 JSON。报告含项目、规则、时间、状态、检查项、输出、失败原因、建议、安全警告、运行环境和耗时。API 支持列表、详情、删除、JSON/Markdown 导出；每次上传产生不同 UUID 和 SHA-256，可区分重复提交。

### 4.6 一次性解释

`ExplanationProvider` 仅接收已脱敏且截断的失败摘要，一次请求返回一次响应，无工具和循环。默认 `TemplateExplanationProvider`；测试使用可注入 `MockExplanationProvider`。本提交不集成任何付费/鉴权 API，因此无需收集或存储 API Key，避免让凭据成为核心路径。未来提供商必须通过系统钥匙串或服务端密钥管理接入，不能进入数据库、日志或前端。

## 5. 非功能需求

- 安全：所有输入不可信；失败默认拒绝；日志按常见凭据模式脱敏。
- 性能：100 MiB 解压上限内，非命令检查在普通学生电脑目标 5 秒内完成。
- 可用性：明确加载、空、错误状态；表单标签；键盘操作；移动端单列布局。
- 可观测性：结构化应用日志包含 run_id/error_code，不记录源码或凭据。
- 可移植性：Python 3.11+、Node 20+；SQLite；Windows/Linux；Docker Compose。
- 可测试性：离线、无真实 LLM、临时数据库/目录；一键脚本非零失败。

## 6. 架构与数据流

React SPA 通过 `/api` 调用 FastAPI。API 将规则交给 RuleService，将 ZIP 交给 SafeExtractor；CheckService 按顺序调用静态 checks 和 Runner；ReportService 持久化 SQLite 并导出。前端由 nginx 提供，Compose 将 `/api` 反向代理到后端。

```text
Browser -> React/nginx -> FastAPI -> RuleService
                              |----> SafeExtractor -> isolated workspace
                              |----> CheckEngine -> static checks
                              |                   -> ControlledRunner
                              |----> ReportStore -> SQLite
                              `----> ExplanationProvider (template/mock only)
```

模块边界：导入层不理解评分；规则层不访问上传内容；检查层不持久化；Runner 不接受网页命令；存储层不执行检查；AI 层不读取项目文件。

## 7. 数据模型

`RuleRecord(id, name, version, language, builtin, source_yaml, created_at)`；`RunRecord(id UUID, project_name, project_hash, rule_id, rule_name, rule_version, status, stage, started_at, finished_at, duration_ms, workspace_path, report_json)`。当前 SQLite 以单表 JSON 报告换取简单迁移；规则快照嵌入报告，历史不受规则更新影响。

## 8. REST API

- `GET /api/health`
- `GET /api/rules`, `POST /api/rules`, `GET /api/rules/template`
- `POST /api/runs`（multipart: project, rule_id）
- `GET /api/runs`, `GET /api/runs/{id}`, `DELETE /api/runs/{id}`
- `GET /api/runs/{id}/report`, `/export.json`, `/export.md`
- `POST /api/runs/{id}/explanation`

错误统一为 `{error:{code,message,details,request_id}}`。422 用于规则/表单验证，413 用于大小限制，400 用于 ZIP，404 用于资源缺失，409 用于运行状态冲突，500 隐藏内部细节。OpenAPI 位于 `/docs`。

## 9. 安全与凭据威胁模型

攻击者可上传压缩炸弹、穿越路径、超大/海量文件、敏感数据和恶意源码；规则作者可尝试注入命令；宿主环境可能含真实凭据。对策分别为流式计数和上限、规范化路径/拒绝链接、Pydantic strict schema、无 shell 参数数组、命令 allow/deny list、环境白名单、默认禁用执行、输出截断与脱敏、工作目录隔离和清理。

本版本没有外部鉴权 API，也不收集 Key，所以通用要求中的钥匙串录入/查看/更新/清除流程不适用。`.env` 只含非秘密运行配置且被忽略；`.env.example` 不含凭据。若未来启用付费 AI，必须先增加 OS keyring/容器 secret 方案和状态管理 UI，不能仅把 Key 存数据库。

## 10. 技术选型

FastAPI/Pydantic/SQLAlchemy/SQLite 提供类型化 API、严格校验和低冷启动成本；React/TypeScript/Vite 提供可测试 SPA；pytest/Ruff/mypy 与 Vitest/ESLint/TypeScript 建立质量门禁；Docker Compose 是分发形态。UI 使用自建 “Notebook” token system（深蓝、暖白、青绿状态色、高对比度、低动画），因为当前 Codex 环境没有 Open Design skill；这项偏离在过程日志中记录。

## 11. 测试与验收

单测覆盖规则、安全解压、检查项、扫描、截断、超时、报告、历史和 provider；API 集成覆盖上传到删除及错误路径；前端覆盖表单、状态、报告、历史、导出和日志折叠；脚本执行端到端 API 演示。CI 分后端、前端、安全和 Docker 配置/构建。

完成判据：UI 可走完整主流程；无网络/Key 可运行；五模块均有测试；所有质量命令通过；Docker 镜像能构建（若本机缺 Docker，必须在限制中明确并由 CI 验证）；文档命令与实测一致。

## 12. 风险与已知限制

- 本机无 Docker，无法本地证明容器运行；保留真实构建结果为待 CI/人工验证项。
- subprocess 不是强沙箱，执行不可信代码默认关闭；启用只适合自己信任的课程样例。
- Windows 下无法可靠阻断子进程网络；网络禁止是规则声明与 Docker 部署策略，不是 subprocess 保证。
- SQLite/本地文件适合单实例；多副本需外部数据库与共享对象存储。
- 文件类型识别按扩展名和规则统计，不做编译器级语义识别。
- Superpowers 与 Open Design 技能未在当前环境提供；过程证据使用等价计划、测试记录和独立上下文审阅，不冒充实际技能调用。

