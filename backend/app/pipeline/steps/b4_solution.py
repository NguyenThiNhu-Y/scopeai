from __future__ import annotations
import asyncio
from app.core import db
from app.llm import complete_with_retry, get_llm_client
from app.llm.gateway import LLMSchemaError
from app.llm.prompts.b4_solution import build_solution_prompt
from app.models import Bid, Question, Requirement
from app.pipeline.steps.common import get_step, mark_failed, publish_error, publish_step, utcnow
from app.privacy import mask_text
from app.schemas.llm_schemas.solution_proposal import SolutionProposal
from app.services.solution_service import choose_solution
from app.pipeline.steps.common import get_step_output


async def run_solution(bid_id: int, client=None) -> dict:
    session = db.SessionLocal()
    step = None
    try:
        step = get_step(session, bid_id, "solution")
        step.status, step.attempts, step.started_at = "running", step.attempts + 1, utcnow()
        session.commit(); publish_step(bid_id, "solution", "running", step.attempts)
        bid = session.get(Bid, bid_id)
        assert bid is not None
        requirements = session.query(Requirement).filter_by(bid_id=bid_id).order_by(Requirement.id).all()
        answers = session.query(Question).filter_by(bid_id=bid_id).order_by(Question.round_no).all()
        context = {
            "bid_id": bid_id,
            "customer_language": bid.customer_language,
            "request": mask_text(bid.request_content),
            "intake": get_step_output(session, bid_id, "intake") or {},
            "questions_and_answers": [{"question": q.question, "answer": q.answer, "round": q.round_no} for q in answers],
            "requirements_summary": {"total": len(requirements), "sample": [{"req_code": r.internal_code, "content": r.content, "priority": r.priority} for r in requirements[:40]]},
            "sample_profile": (get_step_output(session, bid_id, "intake") or {}).get("sample_profile"),
        }
        result = await asyncio.to_thread(complete_with_retry, client or get_llm_client(), SolutionProposal, build_solution_prompt(context), context)
        choose_solution(session, bid_id, result["direction"], result["reason_vi"], "ai_developer", risks=result.get("risks", []), notes=result["architecture_notes_vi"], reliability=result.get("reliability_vi", ""), assumptions=result.get("assumptions_vi", []), excluded_directions=result.get("excluded_directions", []), feasibility=result.get("feasibility", {}), feasibility_score=result.get("feasibility_score"))
        step.output_json, step.status, step.finished_at = result, "completed", utcnow()
        session.commit(); publish_step(bid_id, "solution", "completed", step.attempts)
        return result
    except LLMSchemaError as exc:
        if step: mark_failed(session, step, str(exc))
        publish_error(bid_id, "solution", str(exc)); raise
    finally:
        session.close()
