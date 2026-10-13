"""API schemas Module F — WBS (contract api_contract.md §8.1/§8.2/§8.3)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class WbsItemOut(BaseModel):
    task_code: str
    name_vi: str
    phase: str
    parent_code: str | None
    level: int
    role: str | None
    weight: int | None
    man_day: float | None
    depends_on: list[str]
    sort_order: int
    is_leaf: bool


class WbsTotalsOut(BaseModel):
    man_day: float
    by_phase: dict[str, float]


class WbsCheckOut(BaseModel):
    midpoint: float
    deviation_pct: float
    within_20pct: bool
    pm_qa_ok: bool
    cycle_free: bool
    leaf_max_man_day: float
    leaf_within_limit: bool
    warning: str | None


class WbsTraceOut(BaseModel):
    direction: str
    factors: list[dict[str, Any]]
    factor_product: float
    cap: float
    range: dict[str, float]
    formula: str


class WbsOut(BaseModel):
    items: list[WbsItemOut]
    totals: WbsTotalsOut
    check: WbsCheckOut
    trace: WbsTraceOut


class WbsTaskIn(BaseModel):
    """Task trong op ``add`` — role/man_day bắt buộc khi tạo lá (man_day ≤ 10)."""

    task_code: str = Field(..., min_length=1, max_length=50)
    name_vi: str = Field(..., min_length=1, max_length=300)
    phase: Literal["poc", "mvp", "production"]
    parent_code: str | None = None
    role: Literal[
        "pm", "ba", "brse", "ai_engineer", "backend", "frontend", "qa", "infra"
    ] | None = None
    weight: int | None = Field(default=None, ge=1, le=100)
    man_day: float | None = Field(default=None, ge=0, le=10)
    depends_on: list[str] = Field(default_factory=list, max_length=5)


class WbsChangeIn(BaseModel):
    op: Literal["add", "update", "remove"]
    task: WbsTaskIn | None = None
    task_code: str | None = None
    fields: dict[str, Any] | None = None


class WbsEditIn(BaseModel):
    changes: list[WbsChangeIn] = Field(..., min_length=1)
    by: str | None = None
    note: str | None = None


class RecalculatedOut(BaseModel):
    schedule: dict[str, Any] | None = None
    quotation: None = None  # bổ sung ở M5 — luôn bỏ trống (spec §1.2)


class WbsEditOut(WbsOut):
    recalculated: RecalculatedOut


class WbsSnapshotIn(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)
    by: str | None = None


class WbsSnapshotOut(BaseModel):
    snapshot_id: int
    diff_summary: dict[str, Any] | None