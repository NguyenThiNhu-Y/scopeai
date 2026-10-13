"""Helpers dùng chung cho các bước pipeline (persist + SSE)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import PipelineStep
from app.pipeline.sse import sse_manager


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def get_step(session: Session, bid_id: int, step_key: str) -> PipelineStep:
    step = (
        session.query(PipelineStep)
        .filter(PipelineStep.bid_id == bid_id, PipelineStep.step_key == step_key)
        .one()
    )
    return step


def get_step_output(session: Session, bid_id: int, step_key: str) -> dict | None:
    step = get_step(session, bid_id, step_key)
    return step.output_json


def publish_step(bid_id: int, step_key: str, status: str, attempt: int) -> None:
    sse_manager.publish(
        bid_id,
        "step",
        {"bid_id": bid_id, "step": step_key, "status": status, "attempt": attempt},
    )


def publish_error(bid_id: int, step_key: str, message: str) -> None:
    sse_manager.publish(
        bid_id,
        "error",
        {"bid_id": bid_id, "step": step_key, "status": "failed", "message": message},
    )


def publish_clarify(bid_id: int, round_no: int, questions: list[dict]) -> None:
    sse_manager.publish(
        bid_id,
        "clarify",
        {"bid_id": bid_id, "round": round_no, "questions": questions},
    )


def mark_failed(session: Session, step: PipelineStep, message: str) -> None:
    step.status = "failed"
    step.error_message = message
    step.finished_at = utcnow()
    session.commit()