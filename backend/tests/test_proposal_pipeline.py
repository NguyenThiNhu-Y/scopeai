from app.core import db
from app.models import Bid
from tests.helpers import setup_wbs_bid


def test_proposal_draft_persists_edit_without_llm(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    original = client.get(f"/api/bids/{bid_id}/proposal")
    assert original.status_code == 200
    sections = original.json()["sections"]
    sections["introduction"] = "Nội dung chỉnh sửa giả lập"
    updated = client.put(f"/api/bids/{bid_id}/proposal", json={"sections": sections, "by": "presales"}, headers={"X-User": "presales"})
    assert updated.status_code == 200
    assert client.get(f"/api/bids/{bid_id}/proposal").json()["sections"]["introduction"] == "Nội dung chỉnh sửa giả lập"


def test_proposal_rejects_money_and_man_day(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    sections = client.get(f"/api/bids/{bid_id}/proposal").json()["sections"]
    sections["risks"] = "Giá 100000 VND và 2 man-day"
    response = client.put(f"/api/bids/{bid_id}/proposal", json={"sections": sections})
    assert response.status_code == 400


def test_proposal_after_approval_contains_server_rendered_quotation(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal(), customer_language="ja")
    session = db.SessionLocal()
    bid = session.get(Bid, bid_id)
    bid.status = "waiting_price_approval"
    session.commit()
    session.close()
    approved = client.post(
        f"/api/bids/{bid_id}/approvals/price",
        json={"decision": "approved", "contract_model": "fixed_price"},
        headers={"X-Role": "manager", "X-User": "manager"},
    )
    assert approved.status_code == 200, approved.text
    proposal = client.get(f"/api/bids/{bid_id}/proposal").json()
    assert proposal["price_gate"] == "approved"
    assert "Grand total" in proposal["quotation_markdown"]
