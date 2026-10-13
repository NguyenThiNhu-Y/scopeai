from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.llm_schemas.solution_proposal import FeasibilityScore, SolutionDirection, SolutionRisk


class SolutionChoiceIn(BaseModel):
    direction: SolutionDirection
    reason_vi: str = Field(..., min_length=1, max_length=3000)
    by: str = Field(..., min_length=1, max_length=100)
    assumptions_vi: list[str] = Field(default_factory=list, max_length=5)
    excluded_directions: list[SolutionDirection] = Field(default_factory=list, max_length=5)
    feasibility: dict[str, str] = Field(default_factory=dict)


class SolutionChoiceOut(BaseModel):
    direction: SolutionDirection
    effort_recalculated: bool
    warnings: list[str]


class SolutionCurrentOut(BaseModel):
    direction: SolutionDirection
    reason_vi: str
    selected_by: str | None
    selected_at: datetime
    reliability_vi: str = ""
    assumptions_vi: list[str] = []
    excluded_directions: list[SolutionDirection] = []
    feasibility: dict[str, str] = {}
    risks: list[SolutionRisk | str] = []
    risks_vi: list[str] = []
    feasibility_score: FeasibilityScore | dict | None = None


class EvaluationOut(BaseModel):
    solution_direction: SolutionCurrentOut | None
    warnings: list[dict]
    items: list[dict]
    stats: dict
