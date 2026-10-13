"""Schema output B4; LLM chỉ giải thích hướng, không sinh số."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SolutionDirection(str, Enum):
    NONE = "none"
    TRADITIONAL_ML = "traditional_ml"
    RAG = "rag"
    AGENT = "agent"
    FINE_TUNE = "fine_tune"


class SolutionRisk(BaseModel):
    """Rủi ro định tính; mức điểm chỉ là đánh giá khả thi, không phải effort."""

    model_config = ConfigDict(extra="forbid")

    type_vi: str = Field(..., min_length=1, max_length=200)
    level: int = Field(..., ge=1, le=5)
    description_vi: str = Field(..., min_length=1, max_length=1000)
    mitigation_vi: str = Field(..., min_length=1, max_length=1000)


class FeasibilityScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: int = Field(..., ge=1, le=5)
    reason_vi: str = Field(..., min_length=1, max_length=1000)


class SolutionProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    direction: SolutionDirection
    reason_vi: str = Field(..., min_length=1, max_length=3000)
    risks_vi: list[str] = Field(default_factory=list, max_length=5)
    risks: list[SolutionRisk] = Field(default_factory=list, max_length=6)
    architecture_notes_vi: str = Field(..., min_length=1, max_length=3000)
    reliability_vi: str = Field(default="", max_length=2000)
    assumptions_vi: list[str] = Field(default_factory=list, max_length=5)
    excluded_directions: list[SolutionDirection] = Field(default_factory=list, max_length=5)
    # Feasibility is qualitative LLM guidance; numeric scoring belongs to code.
    feasibility: dict[str, str] = Field(default_factory=dict)
    feasibility_score: FeasibilityScore | None = None

    @field_validator("reason_vi", "architecture_notes_vi")
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Nội dung không được rỗng")
        return value.strip()

    @field_validator("risks_vi")
    @classmethod
    def risks_non_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            raise ValueError("Rủi ro không được rỗng")
        return value

    @field_validator("reliability_vi")
    @classmethod
    def reliability_clean(cls, value: str) -> str:
        return value.strip()

    @field_validator("feasibility")
    @classmethod
    def feasibility_is_qualitative(cls, value: dict[str, str]) -> dict[str, str]:
        allowed = {"technical", "delivery", "operational"}
        if set(value) - allowed or any(not isinstance(v, str) or not v.strip() for v in value.values()):
            raise ValueError("feasibility chỉ được chứa mô tả định tính")
        return value
