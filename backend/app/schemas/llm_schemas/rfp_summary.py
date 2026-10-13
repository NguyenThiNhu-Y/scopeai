"""RfpSummary — schema B1 (Intake) theo llm_pipeline.md §2.

BR-01: schema output LLM KHÔNG chứa trường man-day/giá/ngày.
``extra="forbid"`` chặn mọi trường lạ (vd ``man_day``) ngay ở lớp validate.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

_MAX_WORDS = 500


class RfpSummary(BaseModel):
    """Tóm tắt RFP bằng tiếng Việt — dùng cho demo M1 và bước B1 (M2+)."""

    model_config = ConfigDict(extra="forbid")

    summary_vi: str = Field(..., description="Tóm tắt nội dung RFP bằng tiếng Việt, ≤ 500 từ")
    keywords: list[str] = Field(default_factory=list, max_length=10, description="Tối đa 10 từ khóa")
    notes: list[str] = Field(default_factory=list, max_length=5, description="Tối đa 5 điểm cần chú ý")

    @field_validator("summary_vi")
    @classmethod
    def _summary_not_empty_and_limited(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("summary_vi không được rỗng")
        word_count = len(value.split())
        if word_count > _MAX_WORDS:
            raise ValueError(f"summary_vi vượt {_MAX_WORDS} từ ({word_count} từ)")
        return value