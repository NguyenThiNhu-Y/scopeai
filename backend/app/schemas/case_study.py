"""Schema case study — bảng 3.2 (docs/eval/thiet_ke_danh_gia.md §3.2).

Một case study là dự án đã làm (giả lập) có effort/thời gian THỰC TẾ để so sánh
với hồ sơ đang chào thầu. Schema dùng cho:
- validate khi PUT settings key ``case_studies`` (settings_service);
- validate khi import file (case_study_service).

Nguyên tắc: case thiếu ``actual_man_day`` (vd thua thầu) VẪN lưu được — dùng cho
bài học chào thầu và proposal, nhưng không dùng để so sánh effort (confidence_engine).
"""

from __future__ import annotations

from typing import Literal

import pydantic
from pydantic import BaseModel, ConfigDict, Field


class ManDayByPhase(BaseModel):
    """Effort theo giai đoạn (man-day) — số ≥ 0."""

    model_config = ConfigDict(extra="forbid")

    poc: float = Field(default=0, ge=0)
    mvp: float = Field(default=0, ge=0)
    production: float = Field(default=0, ge=0)


class DurationWeeks(BaseModel):
    """Thời gian thực tế theo giai đoạn (tuần)."""

    model_config = ConfigDict(extra="forbid")

    poc: float = Field(default=0, ge=0)
    go_no_go: float = Field(default=0, ge=0)
    mvp: float = Field(default=0, ge=0)
    production: float = Field(default=0, ge=0)


class TeamPeak(BaseModel):
    """Số người lúc cao điểm theo vai trò."""

    model_config = ConfigDict(extra="forbid")

    pm: int = Field(default=0, ge=0)
    ba: int = Field(default=0, ge=0)
    brse: int = Field(default=0, ge=0)
    ai_engineer: int = Field(default=0, ge=0)
    backend: int = Field(default=0, ge=0)
    frontend: int = Field(default=0, ge=0)
    qa: int = Field(default=0, ge=0)
    infra: int = Field(default=0, ge=0)


class ContractModel(BaseModel):
    """Hình thức hợp đồng theo giai đoạn (vd 準委任 / 請負)."""

    model_config = ConfigDict(extra="forbid")

    poc: str | None = None
    mvp: str | None = None
    production: str | None = None


class BidOutcome(BaseModel):
    """Kết quả chào thầu — dùng cho bài học chào thầu (mục 3.5)."""

    model_config = ConfigDict(extra="forbid")

    result: Literal["won", "lost"]
    bid_month: str | None = None
    contract_model: ContractModel | None = None
    win_reason_vi: str | None = None
    lost_reason_vi: str | None = None


class CaseStudy(BaseModel):
    """Một case study — đúng bảng 3.2 của thiết kế.

    ``actual_man_day`` không bắt buộc: case thua thầu không có effort thực tế
    vẫn lưu được (dùng cho bài học chào thầu), chỉ không dùng để so sánh.
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=300)
    industry: str = Field(..., min_length=1, max_length=200)
    market: Literal["jp", "vn", "other"]
    customer_language: Literal["ja", "vi", "en"]
    direction: Literal["none", "traditional_ml", "rag", "agent", "fine_tune"]
    requirement_count: int = Field(..., ge=1)
    factors: list[str] = Field(default_factory=list)
    year: int | None = None
    public: bool = True
    summary: str = Field(..., min_length=1)
    estimated_man_day: ManDayByPhase | None = None
    actual_man_day: ManDayByPhase | None = None
    actual_duration_weeks: DurationWeeks | None = None
    team_peak: TeamPeak | None = None
    lessons_vi: list[str] = Field(default_factory=list)
    tech: list[str] = Field(default_factory=list)
    bid_outcome: BidOutcome | None = None
    wbs_file: str | None = None


def normalize_case_studies(payload: object) -> tuple[list[dict], list[str]]:
    """Chuẩn hóa danh sách case study; trả ``(hợp lệ, lỗi theo dòng)``.

    Mỗi lỗi là chuỗi tiếng Việt: ``Dòng <n>: cột '<field>': <lý do>``.
    Dùng chung cho PUT settings và import (preview/save).
    """
    if not isinstance(payload, list):
        return [], ["Dữ liệu phải là YAML dạng danh sách"]
    valid: list[dict] = []
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            errors.append(f"Dòng {index}: không phải object")
            continue
        try:
            case = CaseStudy.model_validate(item)
        except pydantic.ValidationError as exc:
            for err in exc.errors():
                loc = ".".join(str(part) for part in err.get("loc", [])) or "root"
                errors.append(f"Dòng {index}: cột '{loc}': {err['msg']}")
            continue
        if case.id in seen_ids:
            errors.append(f"Dòng {index}: id '{case.id}' trùng lặp")
            continue
        seen_ids.add(case.id)
        valid.append(case.model_dump(mode="json"))
    return valid, errors