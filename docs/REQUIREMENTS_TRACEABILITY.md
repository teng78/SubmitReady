# 需求追踪矩阵

| 需求域 | 规格 | 计划 | 代码/测试 | 状态 |
|---|---|---|---|---|
| 安全 ZIP | SPEC 4.1 | T12 | `extractor.py`, backend tests | 完成 |
| 版本化规则 | SPEC 4.2 | T11 | `rules.py`, 3 YAML, validation tests | 完成 |
| 确定性检查 | SPEC 4.3 | T20–T23 | `checks/*`, CheckService tests | 完成 |
| 受控运行 | SPEC 4.4 | T22 | ControlledRunner tests | 降级完成，非沙箱 |
| 报告/历史 | SPEC 4.5 | T30–T31 | API integration + online demo | 完成 |
| 一次性解释 | SPEC 4.6 | T32 | Template/Mock tests | 完成 |
| 六个页面 | SPEC 5/8 | T40–T43 | 6 Vitest + Edge QA | 完成 |
| 测试/CI | SPEC 11 | T50–T54 | 27 tests + CI configs | 本地完成，远程未运行 |
| 分发/冷启动 | SPEC 10–12 | T52/T62 | clean export passed | Docker 未验证 |
| 过程与反思文档 | SPEC 11 | T60–T64 | docs + student-warning draft | 文档完成，学生核验待办 |
