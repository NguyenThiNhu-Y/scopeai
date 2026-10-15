"""Schema output B5 — WBS 3 cấp (llm_pipeline.md §6, ADR-006).

⚠️ BR-01: schema KHÔNG có trường man_day/effort/giá/ngày. LLM chỉ đề xuất
cấu trúc + trọng số; code gán man-day từ bảng chuẩn (wbs_engine).
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WbsPhase(str, Enum):
    POC = "poc"
    MVP = "mvp"
    PRODUCTION = "production"


class WbsRole(str, Enum):
    PM = "pm"
    BA = "ba"
    BRSE = "brse"
    AI_ENGINEER = "ai_engineer"
    BACKEND = "backend"
    FRONTEND = "frontend"
    QA = "qa"
    INFRA = "infra"


class WbsTaskItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_code: str = Field(..., min_length=1, max_length=50)
    name_vi: str = Field(..., min_length=1, max_length=300)
    phase: WbsPhase
    parent_code: str | None = None
    role: WbsRole | None = None
    weight: int | None = Field(default=None, ge=1, le=100)
    depends_on: list[str] = Field(default_factory=list, max_length=5)
    # Truy vết requirement (thiet_ke_danh_gia.md §4): chỉ trên task lá, tối đa 8
    # mã. Đây là PHÂN LOẠI (mã requirement), không phải con số — BR-01 không bị
    # vi phạm (test_llm_schema_no_numbers vẫn pass).
    requirement_codes: list[str] = Field(default_factory=list, max_length=8)


class WbsStructure(BaseModel):
    """Toàn bộ cấu trúc WBS do LLM đề xuất — không chứa con số man-day/ngày."""

    model_config = ConfigDict(extra="forbid")

    tasks: list[WbsTaskItem] = Field(..., min_length=1, max_length=100)
    notes_vi: list[str] = Field(default_factory=list, max_length=5)

    @model_validator(mode="after")
    def validate_structure(self) -> "WbsStructure":
        codes = [t.task_code for t in self.tasks]
        if len(set(codes)) != len(codes):
            raise ValueError("task_code không được trùng lặp")

        by_code = {t.task_code: t for t in self.tasks}
        children: dict[str, list[str]] = {}
        for t in self.tasks:
            if t.parent_code:
                children.setdefault(t.parent_code, []).append(t.task_code)

        def is_leaf(code: str) -> bool:
            return code not in children

        def depth_of(code: str) -> int:
            seen: set[str] = set()
            node = by_code[code]
            depth = 1
            while node.parent_code is not None:
                if node.parent_code in seen:
                    raise ValueError("parent_code tạo vòng cây")
                seen.add(node.parent_code)
                if node.parent_code not in by_code:
                    raise ValueError(f"parent_code '{node.parent_code}' không tồn tại")
                node = by_code[node.parent_code]
                depth += 1
            return depth

        for t in self.tasks:
            if t.parent_code is not None and t.parent_code not in by_code:
                raise ValueError(f"parent_code '{t.parent_code}' của '{t.task_code}' không tồn tại")
            if depth_of(t.task_code) > 3:
                raise ValueError("WBS chỉ được tối đa 3 cấp (nhóm / task / sub-task)")

            leaf = is_leaf(t.task_code)
            if leaf:
                if t.role is None:
                    raise ValueError(f"Task lá '{t.task_code}' bắt buộc có role")
                if t.weight is None:
                    raise ValueError(f"Task lá '{t.task_code}' bắt buộc có weight")
            else:
                if t.role is not None or t.weight is not None:
                    raise ValueError(f"Task nhóm '{t.task_code}' không được có role/weight")
                if t.requirement_codes:
                    raise ValueError(
                        f"Task nhóm '{t.task_code}' không được có requirement_codes "
                        "(chỉ task lá được truy vết requirement)"
                    )

            for code in t.requirement_codes:
                if not code.strip():
                    raise ValueError(f"Task lá '{t.task_code}' có mã requirement rỗng")
                if len(code) > 30:
                    raise ValueError(
                        f"Task lá '{t.task_code}' có mã requirement quá dài ('{code}')"
                    )

            for dep in t.depends_on:
                if dep == t.task_code:
                    raise ValueError(f"Task '{t.task_code}' không thể phụ thuộc chính nó")
                if dep not in by_code:
                    raise ValueError(f"Task '{t.task_code}' phụ thuộc mã không tồn tại '{dep}'")

        # KHÔNG kiểm tra vòng phụ thuộc ở đây: vòng là lỗi NGỮ NGHĨA
        # (check_engine) → retry ≤ 2 → cảnh báo, không fail schema (spec §3.2).
        return self