import json
from sqlalchemy import select
from app.api.errors import pipeline_error
from app.core import db
from app.llm.gateway import complete_with_retry, LLMSchemaError, LLMClient
from app.models import Bid, ProposalDraft, PipelineStep, Question, Requirement, SolutionChoice, WbsItem, Schedule, Evaluation
from app.pipeline.steps.common import get_step_output
from app.schemas.llm_schemas.proposal import ProposalOutput
from app.pipeline.steps.common import utcnow, publish_step, publish_error

# Tên mục proposal theo ngôn ngữ khách — chỉ là gợi ý nội dung (GIÁ TRỊ);
# KHÓA JSON của "sections" luôn là khóa tiếng Anh cố định (xem _build_proposal_prompt).
_SECTION_TITLES: dict[str, dict[str, str]] = {
    "vi": {
        "introduction": "Giới thiệu",
        "requirements_understanding": "Hiểu yêu cầu",
        "solution_overview": "Tổng quan giải pháp",
        "approach": "Cách triển khai",
        "schedule": "Lịch trình",
        "team": "Đội ngũ",
        "assumptions_and_scope": "Giả định và phạm vi ngoài",
        "risks": "Rủi ro",
    },
    "en": {
        "introduction": "Introduction",
        "requirements_understanding": "Requirements understanding",
        "solution_overview": "Solution overview",
        "approach": "Approach",
        "schedule": "Schedule",
        "team": "Team",
        "assumptions_and_scope": "Assumptions and out-of-scope",
        "risks": "Risks",
    },
    "ja": {
        "introduction": "はじめに",
        "requirements_understanding": "ご要件の理解",
        "solution_overview": "提案概要",
        "approach": "進め方",
        "schedule": "スケジュール",
        "team": "体制",
        "assumptions_and_scope": "前提条件・対象外",
        "risks": "リスク",
    },
}

_PROPOSAL_SECTION_ORDER = (
    "introduction",
    "requirements_understanding",
    "solution_overview",
    "approach",
    "schedule",
    "team",
    "assumptions_and_scope",
    "risks",
)


def _build_proposal_prompt(context: dict, customer_language: str) -> str:
    """Dựng prompt B6 — KHÓA "sections" cố định bằng tiếng Anh, chỉ GIÁ TRỊ
    viết theo ngôn ngữ khách (tránh LLM dịch luôn khóa JSON → sai schema)."""
    lang = customer_language or "vi"
    titles = _SECTION_TITLES.get(lang, _SECTION_TITLES["vi"])
    section_lines = "\n".join(
        f'{i}. "{key}" — {titles[key]}'
        for i, key in enumerate(_PROPOSAL_SECTION_ORDER, start=1)
    )
    return f"""Viết proposal theo ngôn ngữ khách {lang}, dựa trên context JSON dưới đây.
Trả về JSON đúng schema ProposalOutput. KHÓA (key) của đối tượng "sections" là CỐ ĐỊNH bằng tiếng Anh, KHÔNG được dịch sang ngôn ngữ khác; chỉ GIÁ TRỊ (value) viết bằng ngôn ngữ khách.
"sections" phải có đủ đúng 8 khóa sau (theo thứ tự):
{section_lines}
Ví dụ đúng:
{{"sections": {{"introduction": "…", "requirements_understanding": "…", "solution_overview": "…", "approach": "…", "schedule": "…", "team": "…", "assumptions_and_scope": "…", "risks": "…"}}}}
Không đưa số tiền, man-day hoặc ngày cụ thể; phần giá phải đúng một dòng {{{{QUOTATION}}}} (token chính xác 2 cặp ngoặc nhọn).
Các mục có thể nằm trong sections, assumptions_phrased và scope_out_phrased theo schema.
Context:\n{json.dumps(context, ensure_ascii=False, indent=2)}"""


def _render_customer_facts(sections: dict[str, str], bid, requirements, solution, schedule) -> dict[str, str]:
    """Replace code-owned facts after LLM validation; the LLM never invents them."""
    lang = bid.customer_language or "vi"
    missing_labels = {"vi": "chưa có dữ liệu", "en": "not yet defined", "ja": "未定"}
    missing_budget = {"vi": "Chưa có dữ liệu ngân sách", "en": "No budget data", "ja": "予算データなし"}
    direction_labels = {
        "vi": {"none": "Không dùng AI", "traditional_ml": "Học máy truyền thống", "rag": "Tra cứu theo tài liệu", "agent": "Trợ lý nhiều bước", "fine_tune": "Tinh chỉnh mô hình"},
        "en": {"none": "No AI", "traditional_ml": "Traditional ML", "rag": "Document retrieval (RAG)", "agent": "Multi-step assistant", "fine_tune": "Fine-tuned model"},
        "ja": {"none": "AIを利用しない", "traditional_ml": "従来型機械学習", "rag": "文書検索（RAG）", "agent": "マルチステップアシスタント", "fine_tune": "モデル微調整"},
    }
    budget = missing_budget.get(lang, missing_budget["vi"])
    if bid.budget_amount is not None:
        budget = f"{bid.budget_amount:,.0f} {bid.budget_currency or bid.display_currency}"
    milestones = {
        "{{CUSTOMER_START}}": bid.customer_schedule_start.isoformat() if bid.customer_schedule_start else missing_labels.get(lang, "chưa có dữ liệu"),
        "{{CUSTOMER_MVP}}": bid.customer_mvp_start.isoformat() if bid.customer_mvp_start else missing_labels.get(lang, "chưa có dữ liệu"),
        "{{CUSTOMER_PRODUCTION}}": bid.customer_production_start.isoformat() if bid.customer_production_start else missing_labels.get(lang, "chưa có dữ liệu"),
        "{{BUDGET}}": budget,
        "{{REQUIREMENT_COUNT}}": str(len(requirements)),
        "{{SOLUTION_DIRECTION}}": direction_labels.get(lang, direction_labels["vi"]).get(solution.direction, "chưa chọn hướng giải pháp") if solution else "chưa chọn hướng giải pháp",
    }
    return {key: _replace_tokens(value, milestones) for key, value in sections.items()}


def _replace_tokens(value: str, tokens: dict[str, str]) -> str:
    for token, replacement in tokens.items():
        value = value.replace(token, replacement)
    return value

async def run_proposal(bid_id: int, client: LLMClient) -> None:
    session = db.SessionLocal()
    try:
        step = session.execute(select(PipelineStep).where(PipelineStep.bid_id == bid_id, PipelineStep.step_key == "proposal")).scalar_one()
        step.status = "running"; step.attempts += 1; step.started_at = utcnow(); session.commit()
        bid = session.get(Bid, bid_id)
        if bid is None:
            raise pipeline_error("Không tìm thấy hồ sơ", {"bid_id": bid_id})
        requirements = session.query(Requirement).filter_by(bid_id=bid_id).order_by(Requirement.id).all()
        choice = session.query(SolutionChoice).filter_by(bid_id=bid_id, superseded_at=None).order_by(SolutionChoice.id.desc()).first()
        schedule = session.query(Schedule).filter_by(bid_id=bid_id).order_by(Schedule.id.desc()).first()
        wbs = session.query(WbsItem).filter_by(bid_id=bid_id).order_by(WbsItem.sort_order, WbsItem.id).all()
        context = {
            "customer_language": bid.customer_language,
            "intake": get_step_output(session, bid_id, "intake") or {},
            "clarification_answers": [{"question": q.question, "answer": q.answer} for q in session.query(Question).filter_by(bid_id=bid_id).all()],
            "solution": {"direction": choice.direction, "reason_vi": choice.reason_vi, "risks_vi": choice.risks_vi, "architecture_notes_vi": choice.architecture_notes_vi} if choice else None,
            "risks": choice.risks_vi if choice else [],
            "wbs_summary": {"by_phase_role": _wbs_summary(wbs)},
            "schedule_by_phase": _schedule_summary(schedule),
            "requirement_coverage": {"total": len(requirements), "evaluated": session.query(Evaluation).filter_by(bid_id=bid_id).count(), "sample": [{"req_code": r.internal_code, "content": r.content} for r in requirements[:40]]},
        }
        prompt = _build_proposal_prompt(context, bid.customer_language)
        try:
            result = complete_with_retry(client, ProposalOutput, prompt, context, max_retries=2)
        except LLMSchemaError as exc:
            step.status = "failed"; step.error_message = str(exc)[:1000]; step.finished_at = utcnow(); session.commit(); publish_error(bid_id,"proposal",str(exc)); raise pipeline_error("Bước proposal thất bại", {"step":"proposal"})
        rendered_sections = _render_customer_facts(result["sections"], bid, requirements, choice, schedule)
        row = session.execute(select(ProposalDraft).where(ProposalDraft.bid_id == bid_id)).scalar_one_or_none()
        if row is None: row = ProposalDraft(bid_id=bid_id, sections=rendered_sections, assumptions_phrased=[], scope_out_phrased=[]); session.add(row)
        else: row.sections=rendered_sections; row.assumptions_phrased=[]; row.scope_out_phrased=[]
        result["sections"] = rendered_sections
        result["assumptions_phrased"] = []
        result["scope_out_phrased"] = []
        step.status="completed"; step.output_json=result; step.finished_at=utcnow(); session.commit(); publish_step(bid_id,"proposal","completed",step.attempts)
    finally: session.close()


def _wbs_summary(items) -> list[dict]:
    summary: dict[tuple[str, str], int] = {}
    for item in items:
        key = (item.phase, item.role)
        summary[key] = summary.get(key, 0) + 1
    return [{"phase": phase, "role": role, "task_count": count} for (phase, role), count in summary.items()]


def _schedule_summary(schedule) -> list[dict]:
    if not schedule or not schedule.tasks_json:
        return []
    return [{"phase": task.get("phase"), "task_count": 1} for task in schedule.tasks_json]
