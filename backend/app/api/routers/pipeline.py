"""Router pipeline — contract api_contract.md §5 (M2)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import Identity, get_db, get_identity
from app.core import db
from app.pipeline import resume
from app.pipeline.orchestrator import orchestrator
from app.pipeline.sse import sse_manager
from app.schemas.api_schemas.pipeline import PipelineStartOut, RerunIn

router = APIRouter(prefix="/bids", tags=["pipeline"])


def get_db_session() -> Session:
    return db.SessionLocal()


@router.post("/{bid_id}/pipeline/start", response_model=PipelineStartOut, status_code=202)
async def start_pipeline(
    bid_id: int, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)
) -> PipelineStartOut:
    """Chạy pipeline (FR-023, §5.1) — trả 202, chạy nền qua asyncio task."""
    result = orchestrator.start(session, bid_id)
    return PipelineStartOut(**result)


@router.get("/{bid_id}/pipeline/events")
async def pipeline_events(
    bid_id: int, identity: Identity = Depends(get_identity)
) -> StreamingResponse:
    """SSE tiến độ (FR-023, §5.2) — replay trạng thái hiện tại + stream live."""
    return StreamingResponse(
        sse_manager.subscribe(bid_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{bid_id}/rerun", response_model=PipelineStartOut, status_code=202)
async def rerun_pipeline(
    bid_id: int, body: RerunIn, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)
) -> PipelineStartOut:
    """Chạy lại từ bước lỗi (FR-023, §5.3) — M2 chỉ hỗ trợ ``from_step=null``."""
    result = resume(
        session,
        bid_id,
        from_step=body.from_step,
        reason=body.reason,
        by=body.by,
    )
    return PipelineStartOut(**result)
