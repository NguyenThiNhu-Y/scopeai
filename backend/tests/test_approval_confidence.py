"""Test duyệt kỹ thuật với độ tin cậy — thiet_ke_danh_gia.md §5.5.

- Mức độ tin cậy Thấp → bắt buộc nhận xét ≥ 10 ký tự mới duyệt được.
- Khi duyệt kỹ thuật, lưu snapshot kết quả độ tin cậy + phiên bản
  case_studies/confidence.yaml vào bản ghi duyệt.
"""

from __future__ import annotations

from app.core import db
from app.models import Approval, Bid
from tests.helpers import setup_wbs_bid


def _set_status(bid_id: int, status: str) -> None:
    session = db.SessionLocal()
    try:
        bid = session.get(Bid, bid_id)
        assert bid is not None
        bid.status = status
        session.commit()
    finally:
        session.close()


def _low_confidence_bid(client) -> int:
    """Hồ sơ có độ tin cậy Thấp: WBS thiếu PM/QA → wbs_checks fail (quan trọng).

    Đợt 14 (C2): mock WBS có nhiều lá PM mỗi phase — xóa TOÀN BỘ lá phase poc
    để chắc chắn pm_qa_ok fail (không còn PM/QA ở poc).
    """
    session = db.SessionLocal()
    try:
        bid_id = setup_wbs_bid(client, session, direction="rag")
    finally:
        session.close()
    session = db.SessionLocal()
    try:
        from app.models import WbsItem

        poc_leaves = (
            session.query(WbsItem)
            .filter_by(bid_id=bid_id, phase="poc")
            .filter(WbsItem.role.isnot(None))
            .all()
        )
        for item in poc_leaves:
            session.delete(item)
        session.commit()
    finally:
        session.close()
    return bid_id


def test_tech_approval_low_confidence_requires_long_comment(client):
    bid_id = _low_confidence_bid(client)
    _set_status(bid_id, "waiting_tech_approval")

    # Không nhận xét → 400.
    resp = client.post(
        f"/api/bids/{bid_id}/approvals/tech",
        json={"decision": "approved"},
        headers={"X-Actor": "developer"},
    )
    assert resp.status_code == 400
    assert "10 ký tự" in resp.json()["error"]["message"]

    # Nhận xét ngắn (< 10 ký tự) → 400.
    resp = client.post(
        f"/api/bids/{bid_id}/approvals/tech",
        json={"decision": "approved", "comment": "Ngắn"},
        headers={"X-Actor": "developer"},
    )
    assert resp.status_code == 400

    # Nhận xét đủ dài → duyệt được.
    resp = client.post(
        f"/api/bids/{bid_id}/approvals/tech",
        json={"decision": "approved", "comment": "Đã rà soát WBS và chấp nhận rủi ro về PM/QA."},
        headers={"X-Actor": "developer"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "waiting_price_approval"


def test_tech_approval_stores_confidence_snapshot(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    _set_status(bid_id, "waiting_tech_approval")
    resp = client.post(
        f"/api/bids/{bid_id}/approvals/tech",
        json={"decision": "approved", "comment": "Hồ sơ đạt các kiểm tra, duyệt."},
        headers={"X-Actor": "developer"},
    )
    assert resp.status_code == 200

    session = db.SessionLocal()
    try:
        row = (
            session.query(Approval)
            .filter_by(bid_id=bid_id, kind="tech")
            .order_by(Approval.id.desc())
            .first()
        )
        assert row is not None
        assert row.snapshot is not None
        assert row.snapshot["confidence"]["level"] in ("high", "medium", "low")
        assert len(row.snapshot["confidence"]["signals"]) == 7
        assert isinstance(row.snapshot["case_studies_version"], int)
        assert isinstance(row.snapshot["confidence_thresholds_version"], int)
    finally:
        session.close()


def test_tech_approval_high_confidence_no_comment_ok(client):
    """Mức không Thấp → không bắt buộc nhận xét (hành vi cũ giữ nguyên)."""
    # Case studies rỗng → analog/history_bias na; xóa WBS → wbs_checks na.
    # Chỉ còn input_completeness warn (thiếu mốc khách) → mức Cao → không cần nhận xét.
    resp = client.put(
        "/api/settings/case_studies",
        json={"yaml_content": "[]", "by": "tester"},
        headers={"X-Actor": "tester"},
    )
    assert resp.status_code == 200
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    session = db.SessionLocal()
    try:
        from app.models import WbsItem

        session.query(WbsItem).filter_by(bid_id=bid_id).delete(synchronize_session=False)
        session.commit()
    finally:
        session.close()
    _set_status(bid_id, "waiting_tech_approval")
    resp = client.post(
        f"/api/bids/{bid_id}/approvals/tech",
        json={"decision": "approved"},
        headers={"X-Actor": "developer"},
    )
    assert resp.status_code == 200