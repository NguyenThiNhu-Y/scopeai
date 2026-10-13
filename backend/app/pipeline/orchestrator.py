"""PipelineOrchestrator — điều phối các bước pipeline thực tế.

M5 triển khai B6 proposal sau WBS; ja_check vẫn pending với ghi chú deferred.
Chặn chạy đồng thời (409 STATE_CONFLICT) và chặn start khi còn câu hỏi
chưa trả lời (409 CLARIFY_PENDING).
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import clarify_pending, state_conflict
from app.core import db
from app.llm import get_llm_client
from app.models import Bid, PipelineStep, Requirement
from app.pipeline import runner
from app.pipeline.sse import sse_manager
from app.pipeline.steps.b1_intake import run_intake
from app.pipeline.steps.b2_gap import run_gap
from app.pipeline.steps.b3_evaluate import run_evaluate
from app.pipeline.steps.b4_solution import run_solution
from app.pipeline.steps.b5_wbs import run_wbs
from app.pipeline.steps.b6_proposal import run_proposal
from app.pipeline.steps.common import utcnow
from app.services.bid_service import STEP_KEYS, get_bid_or_404
from app.services.clarify_service import count_unanswered

logger = logging.getLogger(__name__)

IMPLEMENTED_STEPS = {"intake", "gap", "solution", "evaluate", "wbs", "proposal"}
NOTE_NOT_IMPLEMENTED = "chưa triển khai ở M5"


class PipelineOrchestrator:
    """Singleton điều phối pipeline — mỗi bid một task asyncio."""

    def start(self, session: Session, bid_id: int) -> dict:
        """Đăng ký các bước thực tế, chuyển bid ``analyzing``, spawn pipeline."""
        bid = get_bid_or_404(session, bid_id)
        if runner.is_running(bid_id):
            raise state_conflict("Pipeline đang chạy — vui lòng chờ")

        if bid.status == "waiting_clarification" and count_unanswered(session, bid_id) > 0:
            raise clarify_pending(
                "Còn câu hỏi làm rõ chưa được trả lời — hãy trả lời trước khi chạy pipeline"
            )

        self._ensure_parse_confirmed(session, bid_id)

        self._register_steps(session, bid_id)
        bid.status = "analyzing"
        session.commit()

        runner.spawn(bid_id, self.run(bid_id, from_step=None))
        return runner.current_states(session, bid_id)

    def _register_steps(self, session: Session, bid_id: int) -> None:
        """Tạo các dòng pipeline_steps nếu chưa có (idempotent)."""
        existing = set(
            session.execute(
                select(PipelineStep.step_key).where(PipelineStep.bid_id == bid_id)
            ).scalars()
        )
        for key in STEP_KEYS:
            if key not in existing:
                note = {"note": NOTE_NOT_IMPLEMENTED} if key not in IMPLEMENTED_STEPS else None
                step = PipelineStep(bid_id=bid_id, status="pending", output_json=note)
                step.step_key = key
                session.add(step)
        session.flush()

    async def run(self, bid_id: int, from_step: str | None = None) -> None:
        """Chạy pipeline từ ``from_step`` (mặc định từ đầu). Task asyncio."""
        client = get_llm_client()
        try:
            start_idx = STEP_KEYS.index(from_step) if from_step else 0
            for step_key in STEP_KEYS[start_idx:]:
                if step_key == "intake":
                    await run_intake(bid_id, client)
                elif step_key == "gap":
                    stop = await run_gap(bid_id, client)
                    if stop:
                        # FR-010.3: cần làm rõ → pipeline dừng ở waiting_clarification.
                        return
                elif step_key == "evaluate":
                    # Solution phải được chọn trước để B3 đánh giá theo đúng hướng.
                    eval_session = db.SessionLocal()
                    try:
                        has_requirements = eval_session.query(Requirement).filter_by(bid_id=bid_id).count() > 0
                    finally:
                        eval_session.close()
                    if has_requirements:
                        await run_evaluate(bid_id, client)
                elif step_key == "solution":
                    await run_solution(bid_id, client)
                elif step_key == "wbs":
                    await run_wbs(bid_id, client)
                elif step_key == "proposal":
                    await run_proposal(bid_id, client)
                elif step_key == "ja_check":
                    continue
            await self._finalize(bid_id)
        except Exception as exc:  # noqa: BLE001
            # Bước đã tự đánh dấu failed + phát SSE error với LLMSchemaError;
            # mọi lỗi khác (provider/mạng/DB…) cũng phải đánh dấu failed để
            # hồ sơ không kẹt "analyzing" và rerun có bước để chạy lại (FR-023).
            logger.exception("Pipeline lỗi cho bid %s", bid_id)
            self._mark_running_step_failed(bid_id, exc)

    @staticmethod
    def _ensure_parse_confirmed(session: Session, bid_id: int) -> None:
        """M6 gate: attachment hồ sơ phải được parse và xác nhận trước khi chạy.

        Hồ sơ M1–M5 không có attachment nên vẫn giữ nguyên hành vi cũ. Với hồ sơ
        đã bắt đầu dùng luồng file M6, ``data_readiness`` chỉ được thiết lập bởi
        endpoint ``PUT /parse/confirm``.
        """
        from app.models import Attachment

        has_attachments = session.query(Attachment).filter_by(bid_id=bid_id).count() > 0
        if not has_attachments:
            return
        bid = session.get(Bid, bid_id)
        attachments = session.query(Attachment).filter_by(bid_id=bid_id).all()
        if bid is None or not bid.data_readiness or any(a.parse_status != "ok" for a in attachments):
            raise state_conflict(
                "Cần đọc và xác nhận dữ liệu đính kèm trước khi phân tích",
                {"required": "PUT /api/bids/{id}/parse/confirm", "confirmed": False},
            )

    def _mark_running_step_failed(self, bid_id: int, exc: Exception) -> None:
        """Đánh dấu bước đang ``running`` thành ``failed`` + phát SSE error."""
        session = db.SessionLocal()
        step_key: str | None = None
        try:
            step = (
                session.execute(
                    select(PipelineStep).where(
                        PipelineStep.bid_id == bid_id,
                        PipelineStep.status == "running",
                    )
                )
                .scalars()
                .first()
            )
            if step is None:
                return
            step.status = "failed"
            step.error_message = str(exc)[:1000]
            step.finished_at = utcnow()
            bid = session.get(Bid, bid_id)
            if bid is not None:
                bid.status = "error"
            step_key = step.step_key
            session.commit()
        finally:
            session.close()
        if step_key is not None:
            sse_manager.publish(
                bid_id,
                "error",
                {
                    "bid_id": bid_id,
                    "step": step_key,
                    "status": "failed",
                    "message": str(exc)[:1000],
                },
            )

    async def _finalize(self, bid_id: int) -> None:
        """Semantic done: intake→gap→solution→wbs xong → bid ``waiting_tech_approval``."""
        session = db.SessionLocal()
        try:
            bid = session.get(Bid, bid_id)
            if bid is None:
                raise RuntimeError(f"Hồ sơ {bid_id} không tồn tại khi finalize")
            bid.status = "waiting_tech_approval"
            session.commit()
        finally:
            session.close()
        sse_manager.publish(
            bid_id, "done", {"bid_id": bid_id, "status": "waiting_tech_approval"}
        )


orchestrator = PipelineOrchestrator()
