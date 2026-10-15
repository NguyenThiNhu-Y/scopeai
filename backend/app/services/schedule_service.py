"""ScheduleService — lưu/đọc master schedule (contract §8.4/§8.4a, FR-034).

- Validate ``team_allocation``: mọi role trong WBS phải có headcount ≥ 1
  → thiếu trả 400 kèm ``details.missing_roles`` (BR-04 — không tự đoán số người).
- ``payment_milestones`` tùy chọn → mặc định ``reference/payment.yaml``; tổng ≤ 100.
- Lưu → code tính lại ngay, không gọi AI; ghi changelog ``edit_schedule``.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import state_conflict, validation_error
from app.models import Bid, Changelog, Schedule
from app.schemas.api_schemas.schedule import ScheduleUpdateIn
from app.services.bid_service import get_bid_or_404
from app.services.lock_service import ensure_unlocked
from app.services.reference_service import load_holidays, load_payment
from app.services.schedule_engine import (
    SCHEDULE_FORMULA,
    compute_schedule,
)
from app.services.wbs_engine import enrich_items
from app.services.wbs_service import load_items, item_to_dict

ALLOWED_ROLES = {
    "pm", "ba", "brse", "ai_engineer", "backend", "frontend", "qa", "infra",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def schedule_to_out(sched: Schedule, bid: Bid | None = None) -> dict:
    """Serialize row schedules → response §8.4 (due_date tính từ start_date)."""
    milestones = []
    for m in sched.payment_milestones or []:
        item = dict(m)
        if "due_date" not in item and sched.start_date is not None:
            item["due_date"] = (
                sched.start_date + timedelta(days=int(item.get("due_offset_days", 0)))
            ).isoformat()
        milestones.append(item)
    warning = None
    warnings: list[str] = []
    if sched.deadline_violation:
        warnings.append("Lịch dự kiến cần xác nhận lại phạm vi hoặc nguồn lực")
    if bid is not None:
        if sched.earliest_mvp_start and bid.customer_mvp_start and sched.earliest_mvp_start > bid.customer_mvp_start:
            warnings.append(
                f"Lịch MVP bắt đầu {sched.earliest_mvp_start.isoformat()} trễ hơn "
                f"mốc khách {bid.customer_mvp_start.isoformat()}"
            )
        if sched.earliest_production_start and bid.customer_production_start and sched.earliest_production_start > bid.customer_production_start:
            warnings.append(
                f"Lịch Production bắt đầu {sched.earliest_production_start.isoformat()} trễ hơn "
                f"mốc khách {bid.customer_production_start.isoformat()}"
            )
        if sched.end_date and bid.customer_schedule_end and sched.end_date > bid.customer_schedule_end:
            warnings.append(
                f"Lịch kết thúc {sched.end_date.isoformat()} trễ hơn mốc khách "
                f"{bid.customer_schedule_end.isoformat()}"
            )
    if warnings:
        warning = "; ".join(warnings)
    return {
        "start_date": sched.start_date,
        "buffer_days": sched.buffer_days,
        "go_no_go_gap_working_days": sched.go_no_go_gap_working_days,
        "go_no_go_start": sched.go_no_go_start,
        "go_no_go_end": sched.go_no_go_end,
        "gantt_break_interval": sched.gantt_break_interval,
        "earliest_mvp_start": sched.earliest_mvp_start,
        "earliest_production_start": sched.earliest_production_start,
        "customer_mvp_start": bid.customer_mvp_start if bid else None,
        "customer_production_start": bid.customer_production_start if bid else None,
        "working_calendar": sched.working_calendar,
        "team_allocation": {k: int(v) for k, v in (sched.team_allocation or {}).items()},
        "phase_team_allocation": {
            phase: {role: int(value) for role, value in roles.items()}
            for phase, roles in (sched.phase_team_allocation or {}).items()
        },
        "payment_milestones": milestones,
        "by_role": sched.by_role or {},
        "tasks": sched.tasks_json or [],
        "holidays_applied": sched.holidays_applied or [],
        "end_date": sched.end_date,
        "deadline_violation": sched.deadline_violation,
        "warning": warning,
        "trace": {"formula": SCHEDULE_FORMULA},
        "work_breakdown": sched.tasks_json and _work_breakdown(sched.tasks_json) or {},
    }


def _work_breakdown(tasks: list[dict]) -> dict[str, dict[str, float]]:
    breakdown: dict[str, dict[str, float]] = {}
    for task in tasks:
        phase = task.get("phase")
        role = task.get("role")
        if not phase or not role:
            continue
        phase_rows = breakdown.setdefault(phase, {})
        phase_rows[role] = round(phase_rows.get(role, 0.0) + float(task.get("man_day") or 0), 1)
        phase_rows["total"] = round(
            sum(value for key, value in phase_rows.items() if key != "total"),
            1,
        )
    return breakdown


def get_schedule(session: Session, bid_id: int) -> dict:
    get_bid_or_404(session, bid_id)
    sched = (
        session.execute(
            select(Schedule).where(Schedule.bid_id == bid_id).order_by(Schedule.id.desc())
        )
        .scalars()
        .first()
    )
    if sched is None:
        raise state_conflict("Chưa có lịch — hãy gọi PUT /schedule để tạo lịch")
    return schedule_to_out(sched, session.get(Bid, bid_id))


def _validate_allocation(
    session: Session, bid_id: int, allocation: dict[str, int]
) -> None:
    unknown = set(allocation) - ALLOWED_ROLES
    if unknown:
        raise validation_error(
            f"Vai trò không hợp lệ trong team_allocation: {sorted(unknown)}",
            {"unknown_roles": sorted(unknown)},
        )
    for role, headcount in allocation.items():
        if headcount < 0:
            raise validation_error(
                f"Số người của vai trò '{role}' không được âm", {"role": role}
            )
    items = load_items(session, bid_id)
    if not items:
        raise state_conflict("Chưa có WBS — hãy tạo WBS trước khi lập lịch")
    enriched = enrich_items([item_to_dict(i) for i in items])
    roles_in_wbs = {i["role"] for i in enriched if i["is_leaf"] and i["role"]}
    missing = sorted(r for r in roles_in_wbs if int(allocation.get(r) or 0) < 1)
    if missing:
        raise validation_error(
            "Thiếu số người cho các vai trò xuất hiện trong WBS",
            {"missing_roles": missing},
        )


def _validate_phase_allocation(
    session: Session, bid_id: int, allocation: dict[str, dict[str, int]]
) -> None:
    for phase, roles in allocation.items():
        if phase not in {"poc", "mvp", "production"}:
            raise validation_error("Giai đoạn phân bổ không hợp lệ", {"phase": phase})
        unknown = set(roles) - ALLOWED_ROLES
        if unknown:
            raise validation_error(
                f"Vai trò không hợp lệ trong phân bổ theo giai đoạn: {sorted(unknown)}",
                {"phase": phase, "unknown_roles": sorted(unknown)},
            )
        for role, headcount in roles.items():
            if headcount < 0:
                raise validation_error(
                    f"Số người của vai trò '{role}' không được âm",
                    {"phase": phase, "role": role},
                )


def update_schedule(
    session: Session, bid_id: int, data: ScheduleUpdateIn, by: str
) -> dict:
    """PUT /schedule — lưu tham số, code tính lại lịch ngay (không gọi AI)."""
    bid = get_bid_or_404(session, bid_id)
    ensure_unlocked(bid)

    _validate_allocation(session, bid_id, data.team_allocation)
    if data.phase_team_allocation:
        _validate_phase_allocation(session, bid_id, data.phase_team_allocation)

    milestones = data.payment_milestones
    if milestones is None:
        milestones = load_payment()["milestones"]
    else:
        milestones = [m.model_dump() for m in milestones]
    total_pct = sum(float(m.get("percent", 0)) for m in milestones)
    if total_pct > 100:
        raise validation_error(
            f"Tổng phần trăm mốc thanh toán vượt quá 100 ({total_pct})",
            {"total_percent": total_pct},
        )

    working_calendar = data.working_calendar or (
        "jp" if bid.customer_language == "ja" else "vn"
    )

    items = load_items(session, bid_id)
    enriched = enrich_items([item_to_dict(i) for i in items])
    project_start = data.start_date or bid.customer_schedule_start or date.today()
    result = compute_schedule(
        items=enriched,
        start_date=project_start,
        buffer_days=data.buffer_days,
        team_allocation={k: int(v) for k, v in data.team_allocation.items()},
        phase_team_allocation={
            phase: {role: int(value) for role, value in roles.items()}
            for phase, roles in data.phase_team_allocation.items()
        },
        working_calendar=working_calendar,
        payment_milestones=milestones,
        holidays=load_holidays(),
        go_no_go_gap_working_days=data.go_no_go_gap_working_days,
        customer_poc_end=bid.customer_poc_end,
        customer_mvp_start=bid.customer_mvp_start,
        customer_production_start=bid.customer_production_start,
    )

    sched = (
        session.execute(
            select(Schedule).where(Schedule.bid_id == bid_id).order_by(Schedule.id.desc())
        )
        .scalars()
        .first()
    )
    if sched is None:
        sched = Schedule(bid_id=bid_id)
        session.add(sched)
    sched.start_date = result["start_date"]
    sched.buffer_days = result["buffer_days"]
    sched.working_calendar = result["working_calendar"]
    sched.team_allocation = result["team_allocation"]
    sched.phase_team_allocation = result["phase_team_allocation"]
    sched.payment_milestones = result["payment_milestones"]
    sched.by_role = result["by_role"]
    sched.tasks_json = result["tasks"]
    sched.holidays_applied = result["holidays_applied"]
    sched.end_date = result["end_date"]
    sched.go_no_go_gap_working_days = data.go_no_go_gap_working_days
    sched.go_no_go_start = result["go_no_go_start"]
    sched.go_no_go_end = result["go_no_go_end"]
    sched.earliest_mvp_start = result["earliest_mvp_start"]
    sched.earliest_production_start = result["earliest_production_start"]
    sched.gantt_break_interval = data.gantt_break_interval
    sched.deadline_violation = result["deadline_violation"]
    sched.computed_at = _utcnow()
    sched.updated_by = by

    session.add(Changelog(bid_id=bid_id, actor=by, action="edit_schedule"))
    session.commit()
    session.refresh(sched)
    return schedule_to_out(sched, bid)
