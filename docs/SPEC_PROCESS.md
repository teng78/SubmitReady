# 规约形成过程

## 来源

2026-07-11 完整读取了《通用要求》《B 应用类项目》和《A Coding Agent Harness》。B 与通用要求是验收基线；A 仅用于确认边界：SubmitReady 的固定检查流水线和一次性解释不构成 Agent。

## 三轮关键收敛

1. 原始设想允许构建/测试；安全分析后修订为“受控 subprocess 默认关闭，Docker 为推荐执行环境”，避免把进程超时误称为沙箱。
2. 原始设想允许 OpenAI-compatible Provider；凭据要求审阅后，本提交缩为 Template + Mock，不收集任何 Key。这样核心能力离线可用，未来真实 Provider 必须先加入 keyring/secret 生命周期。
3. 原始规则把命令写成字符串；命令注入分析后改为参数数组、可执行白名单、危险参数拒绝，并禁止网页任意命令。

## 工具与流程偏差

当前 Codex 会话可用技能中没有课程指定的 Superpowers `brainstorming`、`writing-plans`、`test-driven-development`、`requesting-code-review` 和 Open Design。不能如实声称调用这些技能。项目采用显式 SPEC/PLAN、测试先行任务定义、实际红绿结果、独立上下文审阅和双阶段复核作为等价工程证据。当前环境也无法保证“另一种智能体类型”；将使用不继承对话上下文的审阅任务暴露隐含假设，并明确这不等同于课程要求的不同产品/模型。

## 独立冷读结果

在任何实现代码之前，向不继承对话上下文的 Codex 审阅任务仅提供 SPEC/PLAN，并要求拆解 T11/T12、遇到歧义立即停止猜测。它正确指出：YAML 键/默认值/命令策略不精确；文件与数据库同时被描述为规则权威；ZIP 对 UNC、盘符、反斜杠、重复项和特殊文件语义缺失；extractor/API/history 清理职责混杂；T11 与 T50 重复拥有规则资产；任务没有专用验收命令。

修订前：`YAML Schema 版本固定为 1。字段：...`，`SafeExtractor` 只有上限和 Zip Slip 描述。修订后：SPEC 加入完整 YAML 示例、字段范围、命令 allow/deny 策略、文件系统单一权威、跨平台路径拒绝矩阵、稳定错误码和三层清理责任；PLAN 为 T11/T12 补依赖、文件与专用 pytest 命令，并把规则资产从 T50 移到 T11。

限制：审阅者是同一 Codex 产品中的独立上下文，不是课程要求的“不同类型智能体”。它暴露了有效缺陷，但不能替代学生另行使用 Claude/Cursor/Gemini 等完成的正式证据。
