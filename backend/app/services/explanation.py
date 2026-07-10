from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.redaction import safe_output
from app.schemas.report import Explanation


class ExplanationProvider(ABC):
    @abstractmethod
    def explain(self, summary: str) -> Explanation:
        raise NotImplementedError


class TemplateExplanationProvider(ExplanationProvider):
    def explain(self, summary: str) -> Explanation:
        cleaned = safe_output(summary, 4_096)
        if not cleaned.strip():
            text = "辅助建议：当前报告没有构建或测试失败输出，请先处理失败的结构或安全检查项。"
        else:
            text = "辅助建议：请从日志中的第一条错误开始修复，再重新运行检查。错误摘要：" + cleaned
        return Explanation(text=text, auxiliary=True, provider="template")


class MockExplanationProvider(ExplanationProvider):
    def __init__(self, response: str = "Mock auxiliary explanation") -> None:
        self.response = response
        self.calls = 0

    def explain(self, summary: str) -> Explanation:
        self.calls += 1
        safe_output(summary, 4_096)
        return Explanation(text=self.response, auxiliary=True, provider="mock")
