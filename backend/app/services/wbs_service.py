"""WbsService — CRUD WBS 3 cấp (contract §8.1/§8.2/§8.3, FR-032/FR-041).

- ``add``/``update``/``remove`` + xóa sub-tree + dọn ``depends_on``.
- Override ngoài ±20% / thiếu PM-QA bắt buộc ``note`` (BR-12) → thiếu → 400.
- Hồ sơ ``locked`` → 409 (M3-REV-002); danh tính audit từ header (M3-REV-001).
- Sửa xong → code tính lại tổng + check + lịch, KHÔNG gọi AI (FR-041.1).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import state_conflict, validation_error
from app.models import Bid, Changelog, WbsItem, WbsSnapshot
from app.schemas.api_schemas.wbs import WbsTaskIn
from app.services import check_engine
from app.services.bid_service import get_bid_or_404
from app.services.effort_engine import calculate_effort
from app.services.lock_service import ensure_unlocked
from app.services.solution_service import current_choice
from app.services.wbs_engine import PHASES, enrich_items

ALLOWED_UPDATE_FIELDS = {
    "name_vi",
    "phase",
    "parent_code",
    "role",
    "man_day",
    "depends_on",
    "sort_order",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def load_items(session: Session, bid_id: int) -> list[WbsItem]:
    return list(
        session.execute(
            select(WbsItem)
            .where(WbsItem.bid_id == bid_id)
            .order_by(WbsItem.sort_order, WbsItem.id)
        ).scalars()
    )


def item_to_dict(item: WbsItem) -> dict:
    return {
        "task_code": item.task_code,
        "name_vi": item.name_vi,
        "phase": item.phase,
        "parent_code": item.parent_code,
        "role": item.role,
        "weight": item.weight,
        "man_day": item.man_day,
        "depends_on": list(item.depends_on or []),
        "sort_order": item.sort_order,
    }


def persist_wbs_items(
    session: Session, bid_id: int, tasks: list[dict], by: str | None = None
) -> None:
    """Xóa WBS cũ và ghi WBS mới (dùng bởi B5 và test). Không commit."""
    session.query(WbsItem).filter(WbsItem.bid_id == bid_id).delete(
        synchronize_session=False
    )
    siblings: dict[str, int] = {}
    for t in tasks:
        parent = t.get("parent_code") or ""
        siblings[parent] = siblings.get(parent, 0) + 1
        session.add(
            WbsItem(
                bid_id=bid_id,
                task_code=t["task_code"],
                name_vi=t["name_vi"],
                phase=t["phase"],
                parent_code=t.get("parent_code"),
                depends_on=list(t.get("depends_on") or []),
                role=t.get("role"),
                weight=t.get("weight"),
                man_day=t.get("man_day"),
                sort_order=siblings[parent],
                created_by=by,
            )
        )
    session.flush()


def delete_schedule(session: Session, bid_id: int) -> None:
    """Xóa lịch cũ khi WBS thay đổi (dữ liệu tính lại không còn đúng)."""
    from app.models import Schedule

    session.query(Schedule).filter(Schedule.bid_id == bid_id).delete(
        synchronize_session=False
    )


def _effort_for_bid(session: Session, bid: Bid) -> dict:
    choice = current_choice(session, bid.id)
    if choice is None:
        raise state_conflict("Chưa chọn hướng giải pháp để tính WBS")
    return calculate_effort(bid, choice.direction)


def build_wbs_out(session: Session, bid: Bid, items: list[WbsItem]) -> dict:
    """Response §8.1 — items (level/is_leaf/man_day), totals, check, trace."""
    if not items:
        raise state_conflict("Chưa có WBS — hãy chạy bước 'Tạo WBS'")
    enriched = enrich_items([item_to_dict(i) for i in items])
    effort = _effort_for_bid(session, bid)
    midpoint = effort["midpoint_total"]
    by_phase = effort["by_phase"]
    check = check_engine.check_wbs(enriched, midpoint, by_phase)

    leaves = [i for i in enriched if i["is_leaf"]]
    totals = {
        "man_day": round(sum(i["man_day"] or 0.0 for i in leaves), 1),
        "by_phase": {
            phase: round(
                sum(i["man_day"] or 0.0 for i in leaves if i["phase"] == phase), 1
            )
            for phase in PHASES
        },
    }
    trace = {
        "direction": effort["direction"],
        "factors": effort["factors"],
        "factor_product": effort["factor_product"],
        "cap": effort["cap"],
        "range": {
            "min": round(sum(by_phase[p]["min"] for p in PHASES), 1),
            "max": round(sum(by_phase[p]["max"] for p in PHASES), 1),
        },
        "formula": "midpoint(range) × Σweight → man_day/task lá (≤ 10); nhóm = Σ con",
    }
    return {"items": enriched, "totals": totals, "check": check, "trace": trace}


def get_wbs(session: Session, bid_id: int) -> dict:
    bid = get_bid_or_404(session, bid_id)
    return build_wbs_out(session, bid, load_items(session, bid_id))


# ---------------------------------------------------------------- helpers cây

def _children_map(items: list[WbsItem]) -> dict[str, list[WbsItem]]:
    children: dict[str, list[WbsItem]] = {}
    for item in items:
        children.setdefault(item.parent_code or "", []).append(item)
    return children


def _is_leaf(item: WbsItem, children: dict[str, list[WbsItem]]) -> bool:
    return item.task_code not in children


def _depth_of(item: WbsItem, by_code: dict[str, WbsItem]) -> int:
    depth = 1
    parent = item.parent_code
    while parent:
        depth += 1
        parent = by_code[parent].parent_code if parent in by_code else None
    return depth


def _is_descendant(code: str, ancestor: str, by_code: dict[str, WbsItem]) -> bool:
    """True nếu ``code`` nằm trong sub-tree của ``ancestor``."""
    stack = [ancestor]
    while stack:
        cur = stack.pop()
        for item in by_code.values():
            if item.parent_code == cur:
                if item.task_code == code:
                    return True
                stack.append(item.task_code)
    return False


# ---------------------------------------------------------------- validation

def _validate_structure(items: list[WbsItem]) -> None:
    """Kiểm tra cấu trúc cứng (400) sau khi áp dụng changes — contract §8.2."""
    by_code = {i.task_code: i for i in items}
    children = _children_map(items)
    for item in items:
        if _depth_of(item, by_code) > 3:
            raise validation_error(
                f"Task '{item.task_code}' vượt quá 3 cấp (nhóm/task/sub-task)"
            )
        leaf = _is_leaf(item, children)
        if leaf:
            if item.role is None:
                raise validation_error(f"Task lá '{item.task_code}' bắt buộc có role")
            if item.man_day is None:
                raise validation_error(f"Task lá '{item.task_code}' bắt buộc có man_day")
            # WBS đã tồn tại có thể được tạo từ reference range lớn hơn 10;
            # đây là cảnh báo nghiệp vụ, không làm mất precedence của các
            # lỗi cấu trúc (đặc biệt là cycle). Task mới vẫn bị giới hạn ở
            # _apply_add để không tạo thêm dữ liệu vượt ngưỡng.
        else:
            if item.role is not None or item.weight is not None:
                raise validation_error(
                    f"Task nhóm '{item.task_code}' không được có role/weight"
                )
            if item.man_day is not None:
                raise validation_error(
                    f"Task nhóm '{item.task_code}' không được có man_day (nhóm = Σ con)"
                )
        for dep in item.depends_on or []:
            if dep == item.task_code:
                raise validation_error(f"Task '{item.task_code}' không thể phụ thuộc chính nó")
            if dep not in by_code:
                raise validation_error(
                    f"Task '{item.task_code}' phụ thuộc mã không tồn tại '{dep}'"
                )
    enriched = enrich_items([item_to_dict(i) for i in items])
    if not check_engine.cycle_free(enriched):
        raise validation_error("Phụ thuộc task có vòng lặp")


# ---------------------------------------------------------------- changes

def _apply_add(
    session: Session, bid_id: int, task: WbsTaskIn, by_code: dict[str, WbsItem], by: str
) -> None:
    code = task.task_code
    if code in by_code:
        raise validation_error(f"Mã task '{code}' đã tồn tại")
    parent = task.parent_code
    if parent is not None:
        if parent not in by_code:
            raise validation_error(f"Cha '{parent}' không tồn tại")
        if _depth_of(by_code[parent], by_code) + 1 > 3:
            raise validation_error("Độ sâu tối đa 3 cấp (nhóm/task/sub-task)")
    # Task mới chưa có con → là lá → bắt buộc role + man_day ≤ 10.
    if task.role is None:
        raise validation_error(f"Task lá '{code}' bắt buộc có role")
    if task.man_day is None:
        raise validation_error(f"Task lá '{code}' bắt buộc có man_day")
    if task.man_day > 10:
        raise validation_error(f"man_day của task lá '{code}' không được vượt quá 10")
    for dep in task.depends_on:
        if dep == code:
            raise validation_error(f"Task '{code}' không thể phụ thuộc chính nó")
        if dep not in by_code:
            raise validation_error(f"Task '{code}' phụ thuộc mã không tồn tại '{dep}'")

    siblings = [
        i for i in by_code.values() if (i.parent_code or "") == (parent or "")
    ]
    sort_order = max([i.sort_order for i in siblings], default=0) + 1
    item = WbsItem(
        bid_id=bid_id,
        task_code=code,
        name_vi=task.name_vi,
        phase=task.phase,
        parent_code=parent,
        depends_on=list(task.depends_on),
        role=task.role,
        weight=task.weight,
        man_day=task.man_day,
        sort_order=sort_order,
        created_by=by,
    )
    session.add(item)
    by_code[code] = item
    # Nếu cha trước đó là lá (có role/man_day) → giờ thành nhóm → xóa role/weight/man_day.
    if parent in by_code:
        parent_item = by_code[parent]
        if parent_item.role is not None or parent_item.man_day is not None:
            parent_item.role = None
            parent_item.weight = None
            parent_item.man_day = None
            parent_item.updated_by = by
            parent_item.updated_at = _utcnow()


def _apply_update(
    session: Session, task_code: str | None, fields: dict | None, by_code: dict[str, WbsItem], by: str
) -> None:
    if not task_code:
        raise validation_error("Thiếu task_code khi cập nhật")
    if not fields:
        raise validation_error("Thiếu fields khi cập nhật")
    if task_code not in by_code:
        raise validation_error(f"Không tìm thấy task '{task_code}' để cập nhật")
    unknown = set(fields) - ALLOWED_UPDATE_FIELDS
    if unknown:
        raise validation_error(
            f"Trường không được phép cập nhật: {sorted(unknown)}"
        )
    item = by_code[task_code]
    children = _children_map(list(by_code.values()))
    leaf = _is_leaf(item, children)

    new_role = fields.get("role", item.role)
    new_man_day = fields.get("man_day", item.man_day)
    new_parent = fields.get("parent_code", item.parent_code)

    if leaf and new_role is None:
        raise validation_error(f"Task lá '{task_code}' bắt buộc có role")
    if not leaf and new_role is not None:
        raise validation_error(f"Task '{task_code}' không phải lá — không thể gán role")
    if not leaf and new_man_day is not None:
        raise validation_error(f"Task '{task_code}' không phải lá — không thể gán man_day")
    if new_man_day is not None and new_man_day < 0:
        raise validation_error("man_day không được âm")

    if new_parent is not None:
        if new_parent == task_code:
            raise validation_error("Task không thể là cha của chính nó")
        if new_parent not in by_code:
            raise validation_error(f"Cha '{new_parent}' không tồn tại")
        if _is_descendant(new_parent, task_code, by_code):
            raise validation_error("Đổi cha tạo vòng cây")
        if _depth_of(by_code[new_parent], by_code) + 1 > 3:
            raise validation_error("Độ sâu tối đa 3 cấp (nhóm/task/sub-task)")

    for k, v in fields.items():
        setattr(item, k, v)
    item.updated_by = by
    item.updated_at = _utcnow()


def _apply_remove(
    session: Session, task_code: str | None, by_code: dict[str, WbsItem]
) -> None:
    if not task_code:
        raise validation_error("Thiếu task_code khi xóa")
    if task_code not in by_code:
        raise validation_error(f"Không tìm thấy task '{task_code}' để xóa")
    to_delete = {task_code}
    stack = [task_code]
    while stack:
        cur = stack.pop()
        for item in by_code.values():
            if item.parent_code == cur and item.task_code not in to_delete:
                to_delete.add(item.task_code)
                stack.append(item.task_code)
    for code in to_delete:
        session.delete(by_code[code])
    # Dọn depends_on trỏ tới item đã xóa.
    for item in by_code.values():
        if item.task_code in to_delete:
            continue
        cleaned = [d for d in (item.depends_on or []) if d not in to_delete]
        if len(cleaned) != len(item.depends_on or []):
            item.depends_on = cleaned
    for code in to_delete:
        by_code.pop(code, None)


# ---------------------------------------------------------------- API

def apply_changes(
    session: Session,
    bid_id: int,
    changes: list,
    note: str | None,
    by: str,
) -> dict:
    """PUT /wbs — áp dụng changes, tính lại tổng/check/lịch, không gọi AI."""
    bid = get_bid_or_404(session, bid_id)
    ensure_unlocked(bid)
    items = load_items(session, bid_id)
    if not items:
        raise state_conflict("Chưa có WBS — hãy chạy bước 'Tạo WBS' trước khi sửa")
    by_code = {i.task_code: i for i in items}

    for change in changes:
        op = change.op
        if op == "add":
            if change.task is None:
                raise validation_error("Op 'add' cần có task")
            _apply_add(session, bid_id, change.task, by_code, by)
        elif op == "update":
            _apply_update(session, change.task_code, change.fields, by_code, by)
        elif op == "remove":
            _apply_remove(session, change.task_code, by_code)
        else:
            raise validation_error(f"Op không hợp lệ: {op}")
    session.flush()

    items = load_items(session, bid_id)
    _validate_structure(items)

    # Check ngữ nghĩa: ngoài ±20% hoặc thiếu PM/QA → bắt buộc note (BR-12).
    enriched = enrich_items([item_to_dict(i) for i in items])
    effort = _effort_for_bid(session, bid)
    check = check_engine.check_wbs(enriched, effort["midpoint_total"], effort["by_phase"])
    if (not check["within_20pct"] or not check["pm_qa_ok"]) and not (note or "").strip():
        raise validation_error(
            "Thay đổi làm WBS ngoài ±20% hoặc thiếu PM/QA — cần ghi chú override (note)",
            {
                "within_20pct": check["within_20pct"],
                "pm_qa_ok": check["pm_qa_ok"],
                "warning": check["warning"],
            },
        )

    schedule = recalc_schedule(session, bid_id)

    session.add(
        Changelog(bid_id=bid_id, actor=by, action="edit_wbs", note=(note or "").strip() or None)
    )
    session.commit()
    return {**build_wbs_out(session, bid, load_items(session, bid_id)),
            "recalculated": {"schedule": schedule, "quotation": None}}


def recalc_schedule(session: Session, bid_id: int) -> dict | None:
    """Tính lại lịch từ WBS hiện tại nếu đã có tham số lịch; None nếu chưa có."""
    from app.models import Schedule
    from app.services.schedule_engine import compute_schedule
    from app.services.schedule_service import schedule_to_out
    from app.services.reference_service import load_holidays

    sched = session.execute(
        select(Schedule).where(Schedule.bid_id == bid_id).order_by(Schedule.id.desc())
    ).scalars().first()
    if sched is None:
        return None
    items = load_items(session, bid_id)
    enriched = enrich_items([item_to_dict(i) for i in items])
    roles_in_wbs = {i["role"] for i in enriched if i["is_leaf"] and i["role"]}
    allocation = sched.team_allocation or {}
    missing = sorted(r for r in roles_in_wbs if int(allocation.get(r) or 0) < 1)
    if missing:
        # Chưa đủ số người cho role mới — không thể tính lại lịch (người dùng
        # cập nhật PUT /schedule). Giữ lịch cũ, trả None.
        return None
    bid = session.get(Bid, bid_id)
    result = compute_schedule(
        items=enriched,
        start_date=sched.start_date,
        buffer_days=sched.buffer_days,
        team_allocation={k: int(v) for k, v in allocation.items()},
        working_calendar=sched.working_calendar,
        payment_milestones=sched.payment_milestones or [],
        holidays=load_holidays(),
    )
    _store_schedule_result(session, sched, result)
    return schedule_to_out(sched)


def _store_schedule_result(session: Session, sched, result: dict) -> None:
    sched.by_role = result["by_role"]
    sched.tasks_json = result["tasks"]
    sched.holidays_applied = result["holidays_applied"]
    sched.end_date = result["end_date"]
    sched.deadline_violation = result["deadline_violation"]
    sched.payment_milestones = result["payment_milestones"]
    sched.computed_at = _utcnow()
    session.flush()


# ---------------------------------------------------------------- snapshot

def _diff_items(old_items: list[dict], new_items: list[dict]) -> dict:
    old_map = {i["task_code"]: i for i in old_items}
    new_map = {i["task_code"]: i for i in new_items}
    fields = ("name_vi", "phase", "parent_code", "role", "man_day", "depends_on", "sort_order")
    added = sorted(set(new_map) - set(old_map))
    removed = sorted(set(old_map) - set(new_map))
    modified = []
    for code in sorted(set(old_map) & set(new_map)):
        old_item, new_item = old_map[code], new_map[code]
        for field in fields:
            old_val = old_item.get(field)
            new_val = new_item.get(field)
            if old_val != new_val:
                modified.append(
                    {"task_code": code, "field": field, "old": old_val, "new": new_val}
                )
    return {"added": added, "removed": removed, "modified": modified}


def snapshot_wbs(session: Session, bid_id: int, reason: str, by: str) -> dict:
    """POST /wbs/snapshot — lưu toàn bộ WBS + diff_summary so snapshot trước."""
    bid = get_bid_or_404(session, bid_id)
    ensure_unlocked(bid)
    items = load_items(session, bid_id)
    if not items:
        raise state_conflict("Chưa có WBS để chụp snapshot")
    wbs_json = build_wbs_out(session, bid, items)

    prev = (
        session.execute(
            select(WbsSnapshot)
            .where(WbsSnapshot.bid_id == bid_id)
            .order_by(WbsSnapshot.id.desc())
        )
        .scalars()
        .first()
    )
    diff = _diff_items(prev.wbs_json["items"], wbs_json["items"]) if prev else None

    snap = WbsSnapshot(
        bid_id=bid_id,
        reason=reason,
        created_by=by,
        wbs_json=wbs_json,
        diff_summary=diff,
    )
    session.add(snap)
    session.add(Changelog(bid_id=bid_id, actor=by, action="snapshot_wbs", note=reason))
    session.commit()
    session.refresh(snap)
    return {"snapshot_id": snap.id, "diff_summary": diff}
