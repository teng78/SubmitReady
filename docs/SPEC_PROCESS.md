# 规约形成过程

## 来源

2026-07-11 完整读取了《通用要求》《B 应用类项目》和《A Coding Agent Harness》。B 与通用要求是验收基线；A 仅用于确认边界：SubmitReady 的固定检查流水线和一次性解释不构成 Agent。

## 三轮关键收敛

1. 原始设想允许构建/测试；安全分析后修订为“受控 subprocess 默认关闭，Docker 为推荐执行环境”，避免把进程超时误称为沙箱。
2. 原始设想允许 OpenAI-compatible Provider；凭据要求审阅后，本提交缩为 Template + Mock，不收集任何 Key。这样核心能力离线可用，未来真实 Provider 必须先加入 keyring/secret 生命周期。
3. 原始规则把命令写成字符串；命令注入分析后改为参数数组、可执行白名单、危险参数拒绝，并禁止网页任意命令。

## 工具与流程偏差

当前 Codex 会话可用技能中没有课程指定的 Superpowers `brainstorming`、`writing-plans`、`test-driven-development`、`requesting-code-review` 和 Open Design。不能如实声称调用这些技能。项目采用显式 SPEC/PLAN、测试先行任务定义、实际红绿结果、独立上下文审阅和双阶段复核作为等价工程证据。当前环境也无法保证“另一种智能体类型”；将使用不继承对话上下文的审阅任务暴露隐含假设，并明确这不等同于课程要求的不同产品/模型。

## 待完成的独立冷读

在任何实现代码之前，把仅含本 SPEC 与 PLAN 的任务交给无上下文审阅者。记录它的疑问、误读和修订 diff。实现后再补充真实过程，不预写结果。

