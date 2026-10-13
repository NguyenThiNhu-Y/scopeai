"""API schemas cho pipeline — contract api_contract.md §5 (M2)."""

from __future__ import annotations

from pydantic import BaseModel


class StepStateOut(BaseModel):
    """Trạng thái một bước pipeline trong response 202 (contract §5.1)."""

    step_key: str
    status: str


class PipelineStartOut(BaseModel):
    """Response 202 ``POST /pipeline/start`` và ``POST /rerun``."""

    bid_id: int
    status: str
    steps: list[StepStateOut]


class RerunIn(BaseModel):
    """Body ``POST /api/bids/{id}/rerun`` — M2 chỉ hỗ trợ ``from_step=null``."""

    from_step: str | None = None
    reason: str | None = None
    by: str | None = None