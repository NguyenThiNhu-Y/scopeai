"""API schemas — độ tin cậy từng hồ sơ (thiet_ke_danh_gia.md §5.1)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ConfidenceSignal(BaseModel):
    key: str
    label_vi: str
    status: Literal["pass", "warn", "fail", "na"]
    detail_vi: str
    data: dict[str, Any] = Field(default_factory=dict)


class AnalogCase(BaseModel):
    id: str
    title: str
    similarity: float
    # Hướng giải pháp và thị trường của case (thiet_ke_danh_gia.md §7 — bảng
    # "So với dự án tương tự" hiện cột hướng/thị trường).
    direction: str | None = None
    market: str | None = None
    requirement_count: int | None
    actual_man_day: dict[str, float] | None
    actual_total: float
    actual_duration_weeks: dict[str, Any] | None


class HistoryBiasOut(BaseModel):
    direction: Literal["none", "above", "below"] | None
    median_actual_over_estimate: float | None
    case_count: int


class AnalogOut(BaseModel):
    cases: list[AnalogCase]
    actual_total_range: list[float]
    estimate_total: float | None
    effort_midpoint: float | None
    position: Literal["below", "inside", "above", "insufficient"]
    history_bias: HistoryBiasOut


class ConfidenceOut(BaseModel):
    level: Literal["high", "medium", "low"]
    level_label_vi: str
    summary_vi: str
    signals: list[ConfidenceSignal]
    analog: AnalogOut
    thresholds_version: int
    case_studies_version: int