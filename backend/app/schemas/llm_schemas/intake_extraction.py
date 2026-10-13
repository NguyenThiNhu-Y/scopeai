"""IntakeExtraction — schema B1 (Intake) theo llm_pipeline.md §2.

⚠️ BR-01: schema output LLM KHÔNG chứa trường man-day/giá/ngày.
Ngân sách / thời hạn chỉ là GHI CHÚ VĂN BẢN tiếng Việt (``budget_note_vi`` /
``deadline_note_vi``) + cờ boolean. ``extra="forbid"`` chặn trường lạ.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_MAX_OBJECTIVES_WORDS = 300
_MAX_USERS_WORDS = 200
_MAX_DATA_WORDS = 200
_MAX_NOTE_WORDS = 100
_MAX_SUMMARY_WORDS = 500


def _count_words(value: str) -> int:
    return len(value.split())


class IntakeExtraction(BaseModel):
    """Trích xuất cấu trúc 7 nhóm thông tin từ nội dung yêu cầu (đã che PII)."""

    model_config = ConfigDict(extra="forbid")

    objectives_vi: str = Field(..., description="Mục tiêu dự án, tiếng Việt, ≤ 300 từ")
    users_vi: str = Field(..., description="Người dùng / đối tượng sử dụng, tiếng Việt, ≤ 200 từ")
    data_vi: str = Field(..., description="Mô tả dữ liệu liên quan, tiếng Việt, ≤ 200 từ")
    constraints_vi: list[str] = Field(default_factory=list, max_length=5, description="Tối đa 5 ràng buộc")
    budget_mentioned: bool = Field(..., description="Email/RFP có đề cập ngân sách?")
    budget_note_vi: str = Field(default="", description="Ghi chú ngân sách, tiếng Việt, ≤ 100 từ")
    deadline_mentioned: bool = Field(..., description="Email/RFP có đề cập thời hạn?")
    deadline_note_vi: str = Field(default="", description="Ghi chú thời hạn, tiếng Việt, ≤ 100 từ")
    customer_schedule_note_vi: str = Field(default="", description="Mốc lịch khách nêu trong RFP, không suy diễn")
    customer_language_detected: Literal["vi", "en", "ja", "unknown"] = Field(
        ..., description="Ngôn ngữ chính của nội dung yêu cầu"
    )
    summary_vi: str = Field(..., description="Tóm tắt nội dung, tiếng Việt, ≤ 500 từ")
    keywords: list[str] = Field(default_factory=list, max_length=10, description="Tối đa 10 từ khóa")
    notes: list[str] = Field(default_factory=list, max_length=5, description="Tối đa 5 điểm cần chú ý")

    @field_validator("objectives_vi")
    @classmethod
    def _objectives_limited(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("objectives_vi không được rỗng")
        if _count_words(value) > _MAX_OBJECTIVES_WORDS:
            raise ValueError(f"objectives_vi vượt {_MAX_OBJECTIVES_WORDS} từ")
        return value

    @field_validator("users_vi")
    @classmethod
    def _users_limited(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("users_vi không được rỗng")
        if _count_words(value) > _MAX_USERS_WORDS:
            raise ValueError(f"users_vi vượt {_MAX_USERS_WORDS} từ")
        return value

    @field_validator("data_vi")
    @classmethod
    def _data_limited(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("data_vi không được rỗng")
        if _count_words(value) > _MAX_DATA_WORDS:
            raise ValueError(f"data_vi vượt {_MAX_DATA_WORDS} từ")
        return value

    @field_validator("summary_vi")
    @classmethod
    def _summary_limited(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("summary_vi không được rỗng")
        if _count_words(value) > _MAX_SUMMARY_WORDS:
            raise ValueError(f"summary_vi vượt {_MAX_SUMMARY_WORDS} từ")
        return value

    @field_validator("budget_note_vi", "deadline_note_vi", "customer_schedule_note_vi")
    @classmethod
    def _note_limited(cls, value: str) -> str:
        if value and _count_words(value) > _MAX_NOTE_WORDS:
            raise ValueError(f"Ghi chú vượt {_MAX_NOTE_WORDS} từ")
        return value

    @model_validator(mode="after")
    def _notes_required_when_mentioned(self) -> "IntakeExtraction":
        if self.budget_mentioned and not self.budget_note_vi.strip():
            raise ValueError("budget_note_vi bắt buộc khi budget_mentioned=true")
        if self.deadline_mentioned and not self.deadline_note_vi.strip():
            raise ValueError("deadline_note_vi bắt buộc khi deadline_mentioned=true")
        return self
