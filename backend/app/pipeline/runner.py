"""Runner — registry task đang chạy theo bid_id + resume (FR-023).

- Registry ``_running`` dùng cho guard 409 STATE_CONFLICT (chạy đồng thời).
- ``resume(bid_id, from_step=None)``: from_step=null → chạy từ bước ``failed``
  đầu tiên, giữ các bước ``completed`` (FR-023).
- ``resume(from_step="wbs")`` (M4, FR-041.2): tự snapshot WBS cũ, reset bước
  ``wbs`` + downstream (proposal/ja_check), giữ ``evaluate``/``solution``.
"""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import pipeline_error, state_conflict
from app.models import Bid, PipelineStep
from app.services.bid_service import STEP_KEYS, get_bid_or_404
from app.services.lock_service import ensure_unlocked

logger = logging.getLogger(__name__)

_running: dict[int, asyncio.Task] = {}


def is_running(bid_id: int) -> bool:
    return bid_id in _running


def register(bid_id: int, task: asyncio.Task) -> None:
    _running[bid_id] = task


def unregister(bid_id: int) -> None:
    _running.pop(bid_id, None)


def spawn(bid_id: int, coro) -> asyncio.Task:
    """Tạo task asyncio cho pipeline và đăng ký guard 409."""
    task = asyncio.create_task(coro)
    register(bid_id, task)
    task.add_done_callback(lambda _t: unregister(bid_id))
    return task


def _first_failed(session: Session, bid_id: int) -> str | None:
    rows = session.execute(
        select(PipelineStep.step_key, PipelineStep.status).where(
            PipelineStep.bid_id == bid_id
        )
    ).all()
    status_map = {key: status for key, status in rows}
    for key in STEP_KEYS:
        if status_map.get(key) == "failed":
            return key
    return None


def current_states(session: Session, bid_id: int) -> dict:
    bid = session.get(Bid, bid_id)
    steps = (
        session.query(PipelineStep)
        .filter(PipelineStep.bid_id == bid_id)
        .order_by(PipelineStep.id)
        .all()
    )
    return {
        "bid_id": bid_id,
        "status": bid.status if bid else "draft",
        "steps": [{"step_key": s.step_key, "status": s.status} for s in steps],
    }


def resume(
    session: Session,
    bid_id: int,
    from_step: str | None = None,
    reason: str | None = None,
    by: str | None = None,
) -> dict:
    """Chạy lại pipeline từ bước lỗi đầu tiên (hoặc từ ``from_step`` nếu có).

    ``from_step="wbs"`` (M4): snapshot WBS cũ (FR-041.2) + reset wbs và các
    bước sau về pending; giữ ``evaluate``/``solution`` completed.
    """
    bid = get_bid_or_404(session, bid_id)
    ensure_unlocked(bid)
    if is_running(bid_id):
        raise state_conflict("Pipeline đang chạy — không thể chạy lại")

    # Re-run is also a pipeline start and must not bypass the M6 confirmation gate.
    from app.pipeline.orchestrator import orchestrator
    orchestrator._ensure_parse_confirmed(session, bid_id)

    start = from_step
    if start is None:
        start = _first_failed(session, bid_id)
        if start is None:
            raise pipeline_error(
                "Không có bước nào bị lỗi để chạy lại",
                {"step": None},
            )

    step = session.execute(
        select(PipelineStep).where(
            PipelineStep.bid_id == bid_id,
            PipelineStep.step_key == start,
        )
    ).scalar_one_or_none()
    if step is None:
        raise pipeline_error(
            f"Bước '{start}' chưa từng được đăng ký",
            {"step": start},
        )

    if start == "wbs":
        # FR-041.2: snapshot WBS cũ trước khi tạo WBS mới; reset wbs + downstream.
        _snapshot_and_reset_wbs(session, bid_id, reason, by)
    else:
        step.status = "pending"
        step.error_message = None
        step.finished_at = None

    bid = session.get(Bid, bid_id)
    assert bid is not None
    bid.status = "analyzing"
    session.commit()

    spawn(bid_id, orchestrator.run(bid_id, from_step=start))
    return current_states(session, bid_id)


def _snapshot_and_reset_wbs(
    session: Session, bid_id: int, reason: str | None, by: str | None
) -> None:
    """Snapshot WBS cũ (nếu có), xóa dữ liệu WBS/lịch cũ, reset bước wbs + sau."""
    from app.models import WbsItem
    from app.services.wbs_service import (
        delete_schedule,
        load_items,
        snapshot_wbs,
    )

    actor = (by or "anonymous").strip() or "anonymous"
    if load_items(session, bid_id):
        snapshot_wbs(
            session,
            bid_id,
            reason or "Chạy lại từ bước WBS (góp ý)",
            actor,
        )
    # Dữ liệu cũ sẽ được B5 tạo lại — xóa để tránh vi phạm UNIQUE(task_code).
    session.query(WbsItem).filter(WbsItem.bid_id == bid_id).delete(
        synchronize_session=False
    )
    delete_schedule(session, bid_id)

    for key in STEP_KEYS[STEP_KEYS.index("wbs"):]:
        row = session.execute(
            select(PipelineStep).where(
                PipelineStep.bid_id == bid_id, PipelineStep.step_key == key
            )
        ).scalar_one_or_none()
        if row is not None:
            row.status = "pending"
            row.error_message = None
            row.finished_at = None
            if key == "wbs":
                row.output_json = None
