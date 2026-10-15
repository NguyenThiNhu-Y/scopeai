"""ScheduleEngine — tính master schedule bằng code (contract §8.4, ADR-006).

Mô hình (BR-09): phase tuần tự ``poc → mvp → production``; trong cùng phase các
vai trò chạy SONG SONG (mỗi role một cursor riêng), task xếp theo thứ tự topo
của ``depends_on`` (rồi ``sort_order``); duration = ceil(man_day ÷ headcount[role])
ngày làm việc (trừ T7/CN + nghỉ lễ); phase kết thúc khi task cuối của phase xong.
MVP KHÔNG được bắt đầu trước go_no_go_end (khoảng chờ go/no-go sau PoC);
Production bắt đầu sau khi MVP xong. Buffer ở cuối; mốc thanh toán
due_date = start_date + due_offset_days.
"""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import date, timedelta

from app.services.wbs_engine import PHASES

SCHEDULE_FORMULA = (
    "end = start + Σ phase(parallel theo role: max(role_cursor, depends_on_end)) "
    "+ buffer (trừ T7/CN + nghỉ lễ); MVP ≥ go_no_go_end; production sau mvp"
)


def is_working_day(day: date, holidays: set[date]) -> bool:
    return day.weekday() < 5 and day not in holidays


def next_working_day(
    day: date, holidays: set[date], holidays_applied: list[str] | None = None
) -> date:
    day += timedelta(days=1)
    while not is_working_day(day, holidays):
        if holidays_applied is not None and day in holidays:
            if day.isoformat() not in holidays_applied:
                holidays_applied.append(day.isoformat())
        day += timedelta(days=1)
    return day


def to_working_day(
    day: date, holidays: set[date], holidays_applied: list[str] | None = None
) -> date:
    while not is_working_day(day, holidays):
        if holidays_applied is not None and day in holidays:
            if day.isoformat() not in holidays_applied:
                holidays_applied.append(day.isoformat())
        day += timedelta(days=1)
    return day


def add_working_days(
    start: date,
    days: int,
    holidays: set[date],
    holidays_applied: list[str] | None = None,
) -> date:
    """Ngày kết thúc sau ``days`` ngày làm việc (tính cả ``start``)."""
    current = start
    added = 0
    while added < days:
        if is_working_day(current, holidays):
            added += 1
            if added == days:
                return current
        else:
            if holidays_applied is not None and current in holidays:
                if current.isoformat() not in holidays_applied:
                    holidays_applied.append(current.isoformat())
        current += timedelta(days=1)
    return current


def topo_order(tasks: list[dict], by_code: dict[str, dict]) -> list[dict]:
    """Sắp xếp topo theo ``depends_on`` (Kahn), sau đó ``sort_order``."""
    codes = [t["task_code"] for t in tasks]
    indegree = {t["task_code"]: 0 for t in tasks}
    dependents: dict[str, list[str]] = defaultdict(list)
    for t in tasks:
        for dep in t.get("depends_on") or []:
            if dep in by_code and dep in indegree:
                indegree[t["task_code"]] += 1
                dependents[dep].append(t["task_code"])
    ready = sorted(
        [t for t in tasks if indegree[t["task_code"]] == 0],
        key=lambda t: (PHASES.index(t["phase"]), t.get("sort_order") or 0, t["task_code"]),
    )
    order: list[dict] = []
    while ready:
        task = ready.pop(0)
        order.append(task)
        for dep_code in dependents[task["task_code"]]:
            indegree[dep_code] -= 1
            if indegree[dep_code] == 0:
                ready.append(by_code[dep_code])
                ready.sort(
                    key=lambda t: (
                        PHASES.index(t["phase"]),
                        t.get("sort_order") or 0,
                        t["task_code"],
                    )
                )
    if len(order) != len(tasks):
        # Vòng phụ thuộc — trả về thứ tự gốc để không treo (check_engine đã cảnh báo).
        return sorted(tasks, key=lambda t: (PHASES.index(t["phase"]), t.get("sort_order") or 0))
    return order


def compute_schedule(
    *,
    items: list[dict],
    start_date: date,
    buffer_days: int,
    team_allocation: dict[str, int],
    working_calendar: str,
    payment_milestones: list[dict],
    holidays: dict[str, list[str]],
    submission_deadline: date | None = None,
    phase_team_allocation: dict[str, dict[str, int]] | None = None,
    go_no_go_gap_working_days: int = 10,
    customer_poc_end: date | None = None,
    customer_mvp_start: date | None = None,
    customer_production_start: date | None = None,
) -> dict:
    """Tính lịch từ WBS (items đã enrich) × headcount + nghỉ lễ + buffer.

    - Các vai trò trong cùng phase chạy song song: mỗi role giữ một cursor
      riêng; task bắt đầu tại max(cursor của role, end của depends_on, phase_start).
    - MVP phase bắt đầu sau go_no_go_end (khoảng chờ go/no-go sau PoC).
    - Production phase bắt đầu sau khi MVP phase kết thúc.

    Returns:
        dict khớp ``ScheduleOut`` (dates dạng ISO string trong tasks/milestones).
    """
    leaves = [i for i in items if i["is_leaf"] and i.get("role")]
    by_code = {i["task_code"]: i for i in items}
    holiday_set = {
        date.fromisoformat(d)
        for d in holidays.get(working_calendar, [])
    }
    if working_calendar == "both":
        holiday_set |= {date.fromisoformat(d) for d in holidays.get("vn", [])}

    ordered = topo_order(leaves, by_code)
    phase_order = {phase: [t for t in ordered if t["phase"] == phase] for phase in PHASES}

    holidays_applied: list[str] = []
    phase_start = to_working_day(start_date, holiday_set, holidays_applied)
    end_map: dict[str, date] = {}
    tasks_out: list[dict] = []
    by_role: dict[str, dict] = {}
    work_breakdown: dict[str, dict[str, float]] = {}
    phase_end_by_phase: dict[str, date] = {}
    go_no_go_start: date | None = None
    go_no_go_end: date | None = None

    for phase in PHASES:
        phase_tasks = phase_order[phase]
        if phase == "mvp" and phase_end_by_phase.get("poc"):
            # Khoảng chờ go/no-go: sau khi PoC xong + gap ngày làm việc.
            go_no_go_start = next_working_day(
                phase_end_by_phase["poc"], holiday_set, holidays_applied
            )
            go_no_go_end = add_working_days(
                go_no_go_start,
                go_no_go_gap_working_days,
                holiday_set,
                holidays_applied,
            )
            phase_start = max(phase_start, go_no_go_end)
        elif phase == "production"and phase_end_by_phase.get("mvp"):
            phase_start = next_working_day(
                phase_end_by_phase["mvp"], holiday_set, holidays_applied
            )

        # Mốc khách: MVP/Production không được bắt đầu trước mốc khách nêu trong RFP.
        if phase == "mvp"and customer_mvp_start:
            phase_start = max(phase_start, customer_mvp_start)
        elif phase == "production"and customer_production_start:
            phase_start = max(phase_start, customer_production_start)

        # Cursor riêng theo vai trò → các task của các role khác nhau chạy song song.
        role_cursors: dict[str, date] = {}
        phase_end: date | None = None
        for task in phase_tasks:
            role = task["role"]
            phase_allocation = (phase_team_allocation or {}).get(phase, {})
            headcount = int(phase_allocation.get(role) or team_allocation.get(role) or 1)
            duration = math.ceil(float(task["man_day"]) / headcount)
            deps_end = [
                end_map[d]
                for d in task.get("depends_on") or []
                if d in end_map
            ]
            cursor = role_cursors.get(role, phase_start)
            start = max(cursor, *deps_end) if deps_end else cursor
            start = to_working_day(max(start, phase_start), holiday_set, holidays_applied)
            end = add_working_days(start, duration, holiday_set, holidays_applied)
            end_map[task["task_code"]] = end
            role_cursors[role] = next_working_day(end, holiday_set, holidays_applied)
            if phase_end is None or end > phase_end:
                phase_end = end
            tasks_out.append(
                {
                    "task_code": task["task_code"],
                    "phase": task["phase"],
                    "role": role,
                    "man_day": float(task["man_day"]),
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat(),
                }
            )

            role_stat = by_role.setdefault(
                role, {"man_day": 0.0, "headcount": headcount, "duration_days": 0}
            )
            role_stat["man_day"] = round(role_stat["man_day"] + float(task["man_day"]), 1)
            role_stat["duration_days"] += duration
            phase_breakdown = work_breakdown.setdefault(phase, {})
            phase_breakdown[role] = round(
                phase_breakdown.get(role, 0.0) + float(task["man_day"]), 1
            )
            phase_breakdown["total"] = round(
                sum(value for key, value in phase_breakdown.items() if key != "total"),
                1,
            )

        if phase_tasks and phase_end is not None:
            phase_end_by_phase[phase] = phase_end

        # PoC theo kế hoạch khách: nếu khách nêu mốc kết thúc PoC (vd Tokai
        # 2026-12 → 2027-02), PoC dùng đúng khoảng đó — kéo dài task PoC
        # tới mốc khách để go/no-go bắt đầu sau khi PoC kết thúc theo kế hoạch.

        if phase == "poc"and customer_poc_end and phase_end_by_phase.get("poc") and phase_end_by_phase["poc"] < customer_poc_end:
            shift_days = (customer_poc_end - phase_end_by_phase["poc"]).days
            for task in tasks_out:
                if task["phase"] == "poc":
                    task["start_date"] = (
                        date.fromisoformat(task["start_date"]) + timedelta(days=shift_days)
                    ).isoformat()
                    task["end_date"] = (
                        date.fromisoformat(task["end_date"]) + timedelta(days=shift_days)
                    ).isoformat()
                    end_map[task["task_code"]] = date.fromisoformat(task["end_date"])
            phase_end_by_phase["poc"] = customer_poc_end

    last_end = max(end_map.values()) if end_map else start_date
    end_date = add_working_days(last_end, buffer_days, holiday_set, holidays_applied)

    milestones_out = []
    for m in payment_milestones:
        item = dict(m)
        item["due_date"] = (
            start_date + timedelta(days=int(item.get("due_offset_days", 0)))
        ).isoformat()
        milestones_out.append(item)

    mvp_starts = [date.fromisoformat(t["start_date"]) for t in tasks_out if t["phase"] == "mvp"]
    production_starts = [date.fromisoformat(t["start_date"]) for t in tasks_out if t["phase"] == "production"]

    return {
        "start_date": start_date,
        "buffer_days": buffer_days,
        "working_calendar": working_calendar,
        "team_allocation": dict(team_allocation),
        "phase_team_allocation": {
            phase: dict(roles)
            for phase, roles in (phase_team_allocation or {}).items()
        },
        "payment_milestones": milestones_out,
        "by_role": by_role,
        "tasks": tasks_out,
        "holidays_applied": sorted(set(holidays_applied)),
        "end_date": end_date,
        "deadline_violation": False,
        "warning": None,
        "trace": {"formula": SCHEDULE_FORMULA},
        "work_breakdown": work_breakdown,
        "go_no_go_gap_working_days": go_no_go_gap_working_days,
        "go_no_go_start": go_no_go_start,
        "go_no_go_end": go_no_go_end,
        "earliest_mvp_start": min(mvp_starts) if mvp_starts else None,
        "earliest_production_start": min(production_starts) if production_starts else None,
    }
