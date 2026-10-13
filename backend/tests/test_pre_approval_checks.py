from app.core import db
from app.models import Bid
from tests.helpers import setup_wbs_bid


def test_price_approval_returns_checks_report_with_m6_warning(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    session = db.SessionLocal()
    bid = session.get(Bid, bid_id)
    assert bid is not None
    bid.status = "waiting_price_approval"
    session.commit()
    session.close()
    response = client.post(f"/api/bids/{bid_id}/approvals/price", json={"decision": "rejected", "comment": "Cần xem lại"}, headers={"X-Actor": "manager"})
    assert response.status_code == 200
    assert any(item["check"] == "no_missing_requirement" for item in response.json()["checks_report"])


def test_price_approval_blocks_wbs_with_missing_pm_or_qa(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal(), fixture_mode="missing_pm")
    session = db.SessionLocal()
    bid = session.get(Bid, bid_id)
    bid.status = "waiting_price_approval"
    session.commit()
    session.close()
    response = client.post(
        f"/api/bids/{bid_id}/approvals/price",
        json={"decision": "approved", "contract_model": "fixed_price"},
        headers={"X-Actor": "manager"},
    )
    assert response.status_code == 422
