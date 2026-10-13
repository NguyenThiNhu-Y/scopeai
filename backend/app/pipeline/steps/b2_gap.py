"""Bước B2 — Gap detection → câu hỏi làm rõ (llm_pipeline.md §3, FR-010/011)."""

from __future__ import annotations

import asyncio

from app.core import db
from app.llm import complete_with_retry
from app.llm.gateway import LLMSchemaError
from app.llm.prompts.b2_gap import build_gap_prompt
from app.models import Bid, Question, Requirement, Attachment
from pathlib import Path
from app.parsers.docx import extract_text as extract_docx_text
from app.parsers.pdf import extract_text as extract_pdf_text
from app.parsers.text import extract_text
from app.privacy import mask_text
from app.pipeline.steps.common import (
    get_step,
    get_step_output,
    mark_failed,
    publish_clarify,
    publish_error,
    publish_step,
    utcnow,
)
from app.schemas.llm_schemas import GapQuestions
from app.services.bid_service import MAX_CLARIFY_ROUNDS
from app.services.clarify_service import (
    count_rounds_used,
    list_previous_answers,
    save_questions_from_gap,
)

MAX_QUESTIONS_PER_ROUND = 7


def _question_out(q: Question) -> dict:
    return {
        "id": q.id,
        "question": q.question,
        "reason_vi": q.reason_vi,
        "impact": q.impact,
        "related_req_codes": q.related_req_codes or [],
    }


async def run_gap(bid_id: int, client) -> bool:
    """Chạy bước gap.

    Returns:
        True nếu pipeline phải DỪNG (cần làm rõ); False nếu tiếp tục.
    """
    session = db.SessionLocal()
    step = None
    try:
        step = get_step(session, bid_id, "gap")
        step.status = "running"
        step.attempts += 1
        step.started_at = utcnow()
        step.error_message = None
        session.commit()
        publish_step(bid_id, "gap", "running", step.attempts)

        bid = session.get(Bid, bid_id)
        assert bid is not None
        rounds_used = count_rounds_used(session, bid_id)

        # FR-010.4: hết 2 vòng → KHÔNG gọi LLM nữa, presales tự trả lời theo giả định.
        if rounds_used >= MAX_CLARIFY_ROUNDS:
            step.status = "completed"
            step.output_json = {
                "note": "Đã hết số vòng hỏi (2) — không gọi LLM nữa (FR-010.4)"
            }
            step.finished_at = utcnow()
            session.commit()
            publish_step(bid_id, "gap", "completed", step.attempts)
            return False

        intake_output = get_step_output(session, bid_id, "intake") or {}
        previous_answers = list_previous_answers(session, bid_id, rounds_used + 1)
        requirements = session.query(Requirement).filter_by(bid_id=bid_id).order_by(Requirement.id).all()
        requirement_rows = [{"req_code": r.internal_code, "content": r.content, "priority": r.priority, "category": r.category} for r in requirements[:40]]
        rfp_files = []
        for attachment in session.query(Attachment).filter_by(bid_id=bid_id).all():
            try:
                data = Path(attachment.path).read_bytes(); name = attachment.filename.lower()
                if name.endswith(".docx"): text = extract_docx_text(data)
                elif name.endswith(".pdf"): text = extract_pdf_text(data)
                elif name.endswith((".txt", ".md")): text = extract_text(data)
                else: continue
                rfp_files.append({"filename": attachment.filename, "text": mask_text(text)})
            except Exception: continue
        per_file_limit = max(1, 16000 // max(1, len(rfp_files)))
        rfp_files = [{**item, "text": item["text"][:per_file_limit]} for item in rfp_files]
        prompt = build_gap_prompt(
            intake_output, rounds_used, previous_answers, bid.customer_language,
            rfp_files, requirement_rows, len(requirements)
        )
        context = {
            "bid_id": bid_id,
            "customer_language": bid.customer_language,
            "rounds_used": rounds_used,
            "previous_answers": previous_answers,
            "rfp_files": rfp_files,
            "requirements": requirement_rows,
            "requirement_count": len(requirements),
        }

        result = await asyncio.to_thread(
            complete_with_retry, client, GapQuestions, prompt, context
        )

        questions = result["questions"]
        warning: str | None = None
        if len(questions) > MAX_QUESTIONS_PER_ROUND:
            warning = (
                f"LLM trả {len(questions)} câu hỏi — chỉ giữ "
                f"{MAX_QUESTIONS_PER_ROUND} câu đầu"
            )
            questions = questions[:MAX_QUESTIONS_PER_ROUND]

        round_no = rounds_used + 1
        saved = save_questions_from_gap(session, bid_id, round_no, questions)

        if result["needs_clarification"]:
            # FR-010.3: mọi câu hỏi sinh ra đều chặn pipeline → Chờ làm rõ.
            step.status = "waiting_clarification"
            step.output_json = {
                **({"warning": warning} if warning else {}),
                **({"blocking_reason_vi": "Vòng 1 vẫn còn thông tin chặn cần xác nhận."} if round_no == 2 else {}),
            } or None
            session.commit()
            publish_step(bid_id, "gap", "waiting_clarification", step.attempts)
            publish_clarify(bid_id, round_no, [_question_out(q) for q in saved])
            return True

        step.status = "completed"
        step.output_json = {"warning": warning} if warning else None
        step.finished_at = utcnow()
        session.commit()
        publish_step(bid_id, "gap", "completed", step.attempts)
        return False
    except LLMSchemaError as exc:
        if step is not None:
            mark_failed(session, step, str(exc))
        publish_error(bid_id, "gap", str(exc))
        raise
    finally:
        session.close()
