from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.errors import not_found, state_conflict
from app.models import Bid, ProposalDraft, WbsItem, Schedule, Question, Quotation, ExportLog
from app.services.ja_check import check_japanese
from app.exporters.filename import export_filename
from app.exporters.proposal_docx import render_proposal
from app.exporters.estimate_xlsx import render_estimate
from app.exporters.pdf import docx_to_pdf
from app.exporters.bundle import make_bundle

_LABELS = {
    "vi": {"toc":"Mục lục", "quotation":"Báo giá", "introduction":"Giới thiệu", "requirements_understanding":"Hiểu yêu cầu", "solution_overview":"Tổng quan đề xuất", "approach":"Cách triển khai", "schedule":"Lịch trình", "team":"Đội ngũ", "assumptions_and_scope":"Tiền đề và ngoài phạm vi", "risks":"Rủi ro", "assumptions":"Tiền đề và ngoài phạm vi", "scope_out":"Ngoài phạm vi"},
    "en": {"toc":"Table of contents", "quotation":"Quotation", "introduction":"Introduction", "requirements_understanding":"Requirements understanding", "solution_overview":"Solution overview", "approach":"Approach", "schedule":"Schedule", "team":"Team", "assumptions_and_scope":"Assumptions and out of scope", "risks":"Risks", "assumptions":"Assumptions and out of scope", "scope_out":"Out of scope"},
    "ja": {"toc":"目次", "quotation":"見積", "introduction":"はじめに", "requirements_understanding":"ご要件の理解", "solution_overview":"提案概要", "approach":"進め方", "schedule":"スケジュール", "team":"体制", "assumptions_and_scope":"前提条件・対象外", "risks":"リスク", "assumptions":"前提条件・対象外", "scope_out":"対象外"},
}


def _data(session: Session, bid_id: int, llm=None):
    bid = session.get(Bid, bid_id)
    if not bid: raise not_found()
    draft = session.execute(select(ProposalDraft).where(ProposalDraft.bid_id == bid_id)).scalar_one_or_none()
    if not draft: raise state_conflict("Chưa có proposal draft để xuất hồ sơ")
    approved = bool(bid.locked and bid.status == "price_approved")
    quotation = session.execute(select(Quotation).where(Quotation.bid_id == bid_id).order_by(Quotation.id.desc())).scalars().first()
    total = quotation.totals.get("grand_total") if quotation else None
    ja = check_japanese(draft.sections, bid.customer_name, client=llm) if bid.customer_language == "ja" else {"result":"pass", "issues":[]}
    return bid, draft, approved, quotation, total, ja


def artifacts(session: Session, bid_id: int, actor: str, llm=None):
    bid, draft, approved, quotation, total, ja = _data(session, bid_id, llm)
    quotation_text = str(total) if approved and total is not None else "[Presales điền]"
    sections = {key: value.replace("{{QUOTATION}}", quotation_text) for key, value in draft.sections.items()}
    d = {"project_name": bid.project_name, "customer_name": bid.customer_name, "sections": sections, "assumptions": [], "scope_out": [], "labels": _LABELS[bid.customer_language], "quotation": quotation_text, "approved": approved, "total": total,
         "wbs": session.execute(select(WbsItem).where(WbsItem.bid_id == bid_id).order_by(WbsItem.sort_order, WbsItem.id)).scalars().all(),
         "schedule": [], "questions": session.execute(select(Question).where(Question.bid_id == bid_id).order_by(Question.round_no, Question.id)).scalars().all()}
    schedule = session.execute(select(Schedule).where(Schedule.bid_id == bid_id).order_by(Schedule.id.desc())).scalars().first()
    if schedule and schedule.tasks_json:
        d["schedule"] = [
            [str(t.get("start_date", "")), t.get("task_code", ""), str(t.get("end_date", ""))]
            for t in schedule.tasks_json
        ]
    word = render_proposal(d); excel = render_estimate(d); pdf = docx_to_pdf(word)
    names = {"docx": export_filename(bid.customer_name, bid.project_name, "proposal", ext="docx"), "xlsx": export_filename(bid.customer_name, bid.project_name, "estimate", ext="xlsx"), "pdf": export_filename(bid.customer_name, bid.project_name, "proposal", ext="pdf")}
    files = {"docx": (names["docx"], word), "xlsx": (names["xlsx"], excel), "pdf": (names["pdf"], pdf)}
    return bid, approved, ja, files


def log_export(session, bid, kind, actor, approved, ja):
    session.add(ExportLog(bid_id=bid.id, kind=kind, actor=actor, price_gate="approved" if approved else "placeholder", ja_check=ja)); session.commit()
