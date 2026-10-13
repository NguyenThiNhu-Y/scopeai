"""API schemas cho hồ sơ dự thầu — contract api_contract.md §3 (M2)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class BidCreate(BaseModel):
    """Body ``POST /api/bids`` — request_content bắt buộc ≥ 30 ký tự (FR-001.1)."""

    project_name: str = Field(..., min_length=1, max_length=255)
    customer_name: str = Field(..., min_length=1, max_length=255)
    deal_stage: str | None = Field(default=None, max_length=50)
    submission_deadline: date
    customer_language: Literal["vi", "en", "ja"]
    request_content: str = Field(..., min_length=30, description="Nội dung yêu cầu — tối thiểu 30 ký tự")
    budget_amount: float | None = None
    budget_currency: Literal["VND", "JPY", "USD"] | None = None
    customer_schedule_start: date | None = None
    customer_schedule_end: date | None = None
    customer_mvp_start: date | None = None
    customer_production_start: date | None = None
    display_currency: Literal["VND", "JPY", "USD"] | None = None


class BidOut(BaseModel):
    """Response 201 ``POST /api/bids`` (contract §3.1)."""

    id: int
    project_name: str
    customer_name: str
    submission_deadline: date
    customer_schedule_start: date | None = None
    customer_schedule_end: date | None = None
    customer_mvp_start: date | None = None
    customer_production_start: date | None = None
    customer_language: str
    status: str
    locked: bool
    budget_amount: float | None
    budget_currency: str | None
    created_by: str
    created_at: datetime
    display_currency: str = "VND"


class BidListItem(BaseModel):
    """Item trong danh sách ``GET /api/bids`` (contract §3.2)."""

    id: int
    project_name: str
    customer_name: str
    deal_stage: str | None = None
    created_at: datetime
    total_price: float | None = None
    total_price_currency: str | None = None
    status: str
    submission_deadline: date
    customer_language: str
    locked: bool
    updated_at: datetime


class BidListOut(BaseModel):
    """Response 200 ``GET /api/bids``."""

    items: list[BidListItem]
    total: int


class StepStateBrief(BaseModel):
    """Trạng thái một bước trong pipeline_progress.

    ``output_json``/``error_message`` là trường mở rộng (optional, tương thích
    ngược) — UI dùng để hiển thị kết quả phân tích B1 và lỗi bước.
    """

    step_key: str
    status: str
    output_json: dict | None = None
    error_message: str | None = None


class PipelineProgressSummary(BaseModel):
    """Tóm tắt tiến độ pipeline — để UI khôi phục màn hình (spec §2.1)."""

    steps: list[StepStateBrief]
    waiting_clarification: bool
    rounds_used: int
    max_rounds: int


class BidDetailOut(BidOut):
    """Response 200 ``GET /api/bids/{id}`` (contract §3.3)."""

    request_content: str | None = None
    no_requirement_file: bool
    data_readiness: str | None
    pipeline_progress: PipelineProgressSummary
