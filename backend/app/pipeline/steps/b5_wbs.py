"""Bước B5 — WBS 3 cấp (llm_pipeline.md §6, FR-032, ADR-006).

Luồng: prompt (Việt, cấm số/ngày) → gateway → validate WbsStructure →
wbs_engine gán man-day lá từ midpoint → check_engine (lỗi ngữ nghĩa → retry
≤ 2 → cảnh báo, không chặn) → persist wbs_items + output_json.
B5 KHÔNG gọi LLM cho việc tính số; wbs_engine/check_engine không import gateway.
"""

from __future__ import annotations

import asyncio
import math
from datetime import date, timedelta

from sqlalchemy import select

from app.core import db
from app.llm import complete_with_retry
from app.llm.gateway import LLMSchemaError
from app.llm.prompts.b5_wbs import build_wbs_prompt
from app.models import Bid, Requirement
from app.pipeline.steps.common import (
    get_step,
    mark_failed,
    publish_error,
    publish_step,
    utcnow,
)
from app.pipeline.sse import sse_manager
from app.schemas.llm_schemas.wbs_structure import WbsStructure
from app.services import check_engine, wbs_engine
from app.services.effort_engine import calculate_effort
from app.services.solution_service import current_choice
from app.services.wbs_service import delete_schedule, persist_wbs_items
from app.services.schedule_service import update_schedule
from app.schemas.api_schemas.schedule import ScheduleUpdateIn

MAX_SEMANTIC_RETRIES = 2  # retry ≤ 2 (BR-02)


def _feedback(check: dict) -> str:
    return (
        "\n\nCẢNH BÁO: WBS vừa rồi có lỗi ngữ nghĩa: "
        + "; ".join(check_engine.semantic_issues(check))
        + ". Hãy sửa lại cấu trúc/trọng số cho hợp lệ."
    )


async def run_wbs(bid_id: int, client) -> dict:
    session = db.SessionLocal()
    step = None
    try:
        step = get_step(session, bid_id, "wbs")
        step.status = "running"
        step.attempts += 1
        step.started_at = utcnow()
        step.error_message = None
        step.output_json = None
        session.commit()
        publish_step(bid_id, "wbs", "running", step.attempts)

        bid = session.get(Bid, bid_id)
        assert bid is not None
        choice = current_choice(session, bid_id)
        if choice is None:
            raise RuntimeError("Chưa chọn hướng giải pháp — không thể tạo WBS")
        # Truyền session để factor many_requirements được tính — WBS phải dùng
        # CÙNG midpoint với effort engine (Đợt 14 C1).
        effort = calculate_effort(bid, choice.direction, session)

        # Danh sách requirement gọn cho prompt B5 (thiet_ke_danh_gia.md §4):
        # mã + 80 ký tự đầu + nhóm, tối đa 150 dòng. requirements_data dành cho
        # mock/kiểm tra (cấu trúc đầy đủ), không đưa vào prompt.
        requirements = list(
            session.scalars(
                select(Requirement)
                .where(Requirement.bid_id == bid_id)
                .order_by(Requirement.id)
            )
        )
        requirement_lines = [
            f"{r.internal_code} | {r.content.replace(chr(10), ' ')[:80]} | {r.category or ''}"
            for r in requirements
        ]
        context = {
            "bid_id": bid_id,
            "direction": choice.direction,
            "reason_vi": choice.reason_vi,
            "by_phase": effort["by_phase"],
            "midpoint_total": effort["midpoint_total"],
            "customer_language": bid.customer_language,
            "requirements": requirement_lines[:150],
            "requirements_data": [
                {
                    "req_code": r.internal_code,
                    "content": r.content,
                    "category": r.category or "",
                }
                for r in requirements
            ],
        }
        prompt = build_wbs_prompt(context)

        result = await asyncio.to_thread(
            complete_with_retry, client, WbsStructure, prompt, context
        )
        # Chuẩn hóa enum → giá trị plain (str/int) trước khi đưa vào engine.
        result = WbsStructure.model_validate(result).model_dump(mode="json")

        # Bỏ mã requirement không tồn tại (LLM có thể bịa mã) — ghi vào notes.
        existing_codes = {r.internal_code for r in requirements}
        dropped_codes: list[str] = []
        for task in result["tasks"]:
            codes = [str(code) for code in (task.get("requirement_codes") or [])]
            kept = [code for code in codes if code in existing_codes]
            if len(kept) != len(codes):
                dropped_codes.extend(sorted(set(codes) - set(kept)))
                task["requirement_codes"] = kept
        if dropped_codes:
            result.setdefault("notes_vi", []).append(
                "Đã bỏ mã requirement không tồn tại: "
                + ", ".join(sorted(set(dropped_codes)))
            )

        warning: str | None = None
        tasks: list[dict] = []
        for attempt in range(MAX_SEMANTIC_RETRIES + 1):
            tasks = wbs_engine.assign_man_days(result["tasks"], effort["by_phase"])
            enriched = wbs_engine.enrich_items(tasks)
            check = check_engine.check_wbs(
                enriched, effort["midpoint_total"], effort["by_phase"]
            )
            if not check_engine.semantic_issues(check):
                break
            if attempt < MAX_SEMANTIC_RETRIES:
                result = await asyncio.to_thread(
                    complete_with_retry,
                    client,
                    WbsStructure,
                    prompt + _feedback(check),
                    context,
                )
                result = WbsStructure.model_validate(result).model_dump(mode="json")
            else:
                warning = check["warning"]

        persist_wbs_items(session, bid_id, tasks, by="ai_developer")
        delete_schedule(session, bid_id)

        # Master schedule được tạo tự động sau WBS; ngày và headcount là kết quả
        # của code, không phải số do mock/LLM sinh.
        enriched_tasks = wbs_engine.enrich_items(tasks)
        # Lịch mặc định bắt đầu từ mốc khách (RFP) nếu có; fallback 2 tuần tới.
        if bid.customer_schedule_start:
            project_start = bid.customer_schedule_start
        else:
            project_start = date.today() + timedelta(days=14)
            project_start += timedelta(days=(7 - project_start.weekday()) % 7)
        role_effort: dict[str, float] = {}
        for task in enriched_tasks:
            if task.get("is_leaf") and task.get("role"):
                role = task["role"]
                role_effort[role] = role_effort.get(role, 0.0) + float(task["man_day"])
        allocation = {role: max(1, math.ceil(value / 20)) for role, value in role_effort.items()}
        update_schedule(
            session,
            bid_id,
            ScheduleUpdateIn(
                start_date=project_start,
                buffer_days=5,
                working_calendar="jp" if bid.customer_language == "ja" else "vn",
                team_allocation=allocation,
            ),
            by="system",
        )


        step.output_json = {
            "tasks": result["tasks"],
            "notes_vi": result.get("notes_vi", []),
            "warning": warning,
        }
        step.status = "completed"
        step.finished_at = utcnow()
        session.commit()
        publish_step(bid_id, "wbs", "completed", step.attempts)
        if warning:
            sse_manager.publish(
                bid_id,
                "warning",
                {"bid_id": bid_id, "step": "wbs", "message": warning},
            )
        return step.output_json or {}
    except LLMSchemaError as exc:
        if step is not None:
            mark_failed(session, step, str(exc))
        publish_error(bid_id, "wbs", str(exc))
        raise
    finally:
        session.close()
