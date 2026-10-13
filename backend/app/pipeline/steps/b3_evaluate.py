"""B3 — đánh giá requirement sau khi gap đã qua."""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.api.errors import ApiError
from app.core import db
from app.models import Bid, PipelineStep, Requirement, SolutionChoice
from app.pipeline.steps.common import get_step, mark_failed, publish_error, publish_step, utcnow
from app.services.evaluation_service import evaluate


async def run_evaluate(bid_id: int, client) -> dict:
    session = db.SessionLocal()
    step = None
    try:
        step = get_step(session, bid_id, "evaluate")
        step.status = "running"
        step.attempts += 1
        step.started_at = utcnow()
        step.error_message = None
        session.commit()
        publish_step(bid_id, "evaluate", "running", step.attempts)

        requirements = list(session.scalars(select(Requirement).where(Requirement.bid_id == bid_id)))
        choice = session.query(SolutionChoice).filter_by(bid_id=bid_id, superseded_at=None).order_by(SolutionChoice.id.desc()).first()
        if not requirements:
            step.status = "completed"
            step.output_json = {"total": 0, "evaluated": 0, "warnings": []}
        else:
            bid = session.get(Bid, bid_id)
            result = await asyncio.to_thread(
                evaluate,
                session,
                bid_id,
                choice.direction if choice else None,
                client,
            )
            result["evaluated"] = len(requirements) - sum(
                len(w.get("codes", [])) for w in result.get("warnings", [])
            )
            step.output_json = result
            step.status = "completed"
        step.finished_at = utcnow()
        session.commit()
        publish_step(bid_id, "evaluate", "completed", step.attempts)
        return step.output_json or {}
    except Exception as exc:
        if step is not None:
            mark_failed(session, step, str(exc))
        publish_error(bid_id, "evaluate", str(exc))
        raise
    finally:
        session.close()
