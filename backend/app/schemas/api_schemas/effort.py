from __future__ import annotations

from pydantic import BaseModel
from app.schemas.llm_schemas.solution_proposal import SolutionDirection


class PhaseRange(BaseModel):
    min: float
    max: float


class AppliedFactor(BaseModel):
    key: str
    value: float
    reason: str


class EffortTrace(BaseModel):
    table_version: int
    source: str
    formula: str
    raw_factor_product: float
    capped_factor_product: float


class EffortOut(BaseModel):
    direction: SolutionDirection
    factors: list[AppliedFactor]
    factor_product: float
    cap: float
    by_phase: dict[str, PhaseRange]
    midpoint_total: float
    trace: EffortTrace
