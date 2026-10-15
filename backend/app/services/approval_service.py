from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.api.errors import state_conflict, validation_error, check_failed
from app.models import Approval, Bid, Changelog
from app.services.bid_service import get_bid_or_404
from app.services.quotation_engine import calculate_quotation
from app.services.proposal_service import get_or_create
from app.services.wbs_service import load_items, item_to_dict
from app.services.wbs_engine import enrich_items
from app.services.check_engine import check_wbs
from app.services.confidence_service import get_confidence
from app.services.effort_engine import calculate_effort

def _checks(session, bid):
    items = enrich_items([item_to_dict(i) for i in load_items(session, bid.id)])
    effort = calculate_effort(bid, "rag")
    result = check_wbs(items, effort["midpoint_total"], effort["by_phase"])
    report = [
        {"check": "schema_valid", "status": "pass" if items else "fail"},
        {"check": "effort_within_20pct", "status": "pass" if result["within_20pct"] else "fail", "detail": result["warning"]},
        {"check": "pm_qa_present", "status": "pass" if result["pm_qa_ok"] else "fail"},
        {"check": "cycle_free", "status": "pass" if result["cycle_free"] else "fail"},
        {"check": "leaf_within_limit", "status": "pass" if result["leaf_within_limit"] else "warning", "detail": result["warning"] if not result["leaf_within_limit"] else None},
        {"check":"no_missing_requirement","status":"warning","detail":"Deferred to M6 — no requirement matrix"},
    ]
    return report
def tech(session, bid_id, decision, actor, comment=None, skip_reason=None):
    bid = get_bid_or_404(session,bid_id)
    if bid.status not in ("waiting_tech_approval", "rejected"): raise state_conflict("Hồ sơ chưa sẵn sàng duyệt kỹ thuật")
    if decision == "rejected" and not (comment or "").strip(): raise validation_error("Từ chối duyệt kỹ thuật phải có lý do")
    if decision == "skip" and not (skip_reason or "").strip(): raise validation_error("Bỏ qua duyệt kỹ thuật phải có lý do")
    # Mức độ tin cậy Thấp → bắt buộc nhận xét ≥ 10 ký tự (thiet_ke_danh_gia.md §5.5).
    confidence = get_confidence(session, bid_id)
    if confidence["level"] == "low":
        review = (comment or skip_reason or "").strip()
        if len(review) < 10:
            raise validation_error(
                "Độ tin cậy ước lượng ở mức Thấp — cần nhận xét kỹ thuật tối thiểu 10 ký tự",
                {"min_length": 10, "level": "low"},
            )
    approved = decision in ("approved", "skip"); bid.status = "waiting_price_approval" if approved else "rejected"
    row = Approval(bid_id=bid_id,kind="tech",approver=actor,status="approved" if approved else "rejected",reason=comment or skip_reason,decided_at=datetime.now(timezone.utc))
    # Lưu snapshot độ tin cậy + phiên bản bảng chuẩn vào bản ghi duyệt (§5.5).
    row.snapshot = {
        "confidence": confidence,
        "case_studies_version": confidence.get("case_studies_version"),
        "confidence_thresholds_version": confidence.get("thresholds_version"),
    }
    session.add(row); session.add(Changelog(bid_id=bid_id,actor=actor,action="approve_tech" if approved else "reject_tech",note=comment or skip_reason)); session.commit()
    return {"status":bid.status,"locked":bid.locked,"approval_id":row.id}
def price(session,bid_id,data,actor):
    bid=get_bid_or_404(session,bid_id)
    if bid.status != "waiting_price_approval": raise state_conflict("Hồ sơ chưa qua duyệt kỹ thuật")
    if data.decision == "rejected" and not (data.comment or "").strip(): raise validation_error("Từ chối duyệt giá phải có lý do")
    report=_checks(session,bid)
    if data.decision == "approved" and any(x["status"] == "fail" for x in report): raise check_failed("Kiểm tra trước duyệt thất bại", {"checks_report":report})
    if data.decision == "rejected": bid.status="rejected"
    else:
        calculate_quotation(
            session,
            bid_id,
            data.contract_model,
            data.contingency_percent,
            data.onsite_percent,
            data.price_to_win_percent,
            data.tm_months,
            data.odc_fte,
            data.odc_months,
            by=actor,
        )
        bid.status="price_approved"; bid.locked=True; bid.lock_reason="Đã duyệt giá"
    row=Approval(bid_id=bid_id,kind="price",approver=actor,status=data.decision,reason=data.comment,checks_report=report,decided_at=datetime.now(timezone.utc)); session.add(row); session.add(Changelog(bid_id=bid_id,actor=actor,action="approve_price" if data.decision == "approved" else "reject_price",note=data.comment)); session.commit()
    return {"status":bid.status,"locked":bid.locked,"checks_report":report}
