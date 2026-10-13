"""GapQuestions — schema B2 (Gap detection) theo llm_pipeline.md §3.

BR-01: schema KHÔNG chứa trường man-day/giá/ngày — chỉ câu hỏi + lý do + mức ảnh hưởng.
M2: ``related_req_codes`` luôn rỗng (chưa có bảng requirements — M6).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GapQuestionItem(BaseModel):
    """Một câu hỏi làm rõ do LLM đề xuất."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(..., description="Nội dung câu hỏi bằng NGÔN NGỮ KHÁCH (vi/en/ja)")
    reason_vi: str = Field(..., description="Lý do hỏi bằng tiếng Việt")
    impact: Literal["solution", "effort", "price"] = Field(
        ..., description="Mức ảnh hưởng: giải pháp / effort / giá"
    )
    related_req_codes: list[str] = Field(
        default_factory=list, description="M2 luôn rỗng — chưa có bảng requirements"
    )

    @model_validator(mode="after")
    def _non_empty(self) -> "GapQuestionItem":
        if not self.question.strip():
            raise ValueError("question không được rỗng")
        if not self.reason_vi.strip():
            raise ValueError("reason_vi không được rỗng")
        return self


class GapQuestions(BaseModel):
    """Output B2 — có cần làm rõ hay không + danh sách câu hỏi (≤ 7, kiểm tra code)."""

    model_config = ConfigDict(extra="forbid")

    needs_clarification: bool = Field(..., description="True nếu thiếu thông tin cần hỏi")
    questions: list[GapQuestionItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def _consistent(self) -> "GapQuestions":
        if not self.needs_clarification and self.questions:
            raise ValueError("needs_clarification=false nhưng vẫn có câu hỏi")
        if self.needs_clarification and not self.questions:
            raise ValueError("needs_clarification=true nhưng không có câu hỏi nào")
        return self