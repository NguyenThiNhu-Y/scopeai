from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.errors import not_found, state_conflict
from app.models import Bid, ProposalDraft, WbsItem, Schedule, Question, Quotation, ExportLog
from app.services.ja_check import check_japanese
from app.services.settings_service import get_optional_setting
from app.exporters.common import PRICE_PLACEHOLDER, format_money
from app.exporters.filename import export_filename
from app.exporters.proposal_docx import render_proposal
from app.exporters.proposal_pptx import render_slides
from app.exporters.estimate_xlsx import render_estimate
from app.exporters.pdf import docx_to_pdf

# Bundle order is part of the deterministic contract.
BUNDLE_KINDS = ("docx", "xlsx", "pdf", "pptx")
_FILE_SPEC = {
    "docx": ("proposal", "docx"),
    "xlsx": ("estimate", "xlsx"),
    "pdf": ("proposal", "pdf"),
    "pptx": ("slides", "pptx"),
}
# Keys of quotation totals that carry no money and may be shown before price approval.
_NON_MONEY_KEYS = ("phase_man_days", "tax_percent", "odc_fte_months")


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


def _quotation_detail(quotation: Quotation | None, approved: bool) -> dict | None:
    if quotation is None:
        return None
    totals = quotation.totals or {}
    detail = {
        "contract_model": quotation.contract_model,
        "tax_mode": quotation.tax_mode,
        "valid_until": quotation.valid_until.isoformat() if quotation.valid_until else None,
    }
    if approved:
        return {**detail, **totals}
    detail.update({key: totals.get(key) for key in _NON_MONEY_KEYS})
    detail["by_role"] = {role: {"man_day": value.get("man_day")} for role, value in (totals.get("by_role") or {}).items()}
    detail["payment_plan"] = [{k: v for k, v in item.items() if k != "amount"} for item in totals.get("payment_plan") or []]
    return detail


def build_export_data(session: Session, bid_id: int, llm=None, export_date: str | None = None):
    bid, draft, approved, quotation, total, ja = _data(session, bid_id, llm)
    currency = bid.display_currency or "VND"
    quotation_text = format_money(total, currency) if approved and total is not None else PRICE_PLACEHOLDER
    sections = {key: value.replace("{{QUOTATION}}", quotation_text) for key, value in draft.sections.items()}
    schedule = session.execute(select(Schedule).where(Schedule.bid_id == bid_id).order_by(Schedule.id.desc())).scalars().first()
    schedule_data = None
    if schedule and schedule.tasks_json:
        schedule_data = {
            "start_date": schedule.start_date.isoformat() if schedule.start_date else None,
            "end_date": schedule.end_date.isoformat() if schedule.end_date else None,
            "tasks": list(schedule.tasks_json),
            "payment_milestones": [
                {**m, "due_date": m.get("due_date") or (
                    (schedule.start_date + timedelta(days=int(m.get("due_offset_days", 0)))).isoformat() if schedule.start_date else None)}
                for m in schedule.payment_milestones or []
            ],
        }
    company = get_optional_setting(session, "company") or {}
    data = {
        "project_name": bid.project_name, "customer_name": bid.customer_name, "company_name": company.get("company_name") or "",
        "customer_language": bid.customer_language, "currency": currency, "export_date": export_date or date.today().isoformat(),
        "sections": sections, "assumptions": list(draft.assumptions_phrased or []), "scope_out": list(draft.scope_out_phrased or []),
        "quotation": quotation_text, "approved": approved, "total": total if approved else None,
        "quotation_detail": _quotation_detail(quotation, approved),
        "wbs": session.execute(select(WbsItem).where(WbsItem.bid_id == bid_id).order_by(WbsItem.sort_order, WbsItem.id)).scalars().all(),
        "schedule": schedule_data,
        "customer_deadline": bid.customer_schedule_end.isoformat() if bid.customer_schedule_end else None,
        "questions": session.execute(select(Question).where(Question.bid_id == bid_id).order_by(Question.round_no, Question.id)).scalars().all(),
    }
    return bid, approved, ja, data


def render_files(bid, data: dict, kinds) -> dict[str, tuple[str, bytes]]:
    """Render only the requested artifacts; the Word file is reused for PDF."""
    files: dict[str, tuple[str, bytes]] = {}
    word = None
    for kind in kinds:
        if kind in ("docx", "pdf"):
            word = word or render_proposal(data)
            body = word if kind == "docx" else docx_to_pdf(word)
        elif kind == "xlsx":
            body = render_estimate(data)
        else:
            body = render_slides(data)
        label, ext = _FILE_SPEC[kind]
        files[kind] = (export_filename(bid.customer_name, bid.project_name, label, export_date=data["export_date"], ext=ext), body)
    return files


def artifacts(session: Session, bid_id: int, llm=None, kinds=BUNDLE_KINDS):
    bid, approved, ja, data = build_export_data(session, bid_id, llm)
    return bid, approved, ja, render_files(bid, data, kinds), data["export_date"]


def log_export(session, bid, kind, actor, approved, ja):
    session.add(ExportLog(bid_id=bid.id, kind=kind, actor=actor, price_gate="approved" if approved else "placeholder", ja_check=ja)); session.commit()
