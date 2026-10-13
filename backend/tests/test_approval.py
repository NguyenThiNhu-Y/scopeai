from app.core import db
from app.models import Bid
from tests.helpers import setup_wbs_bid


def _set_status(bid_id, status):
    session = db.SessionLocal()
    bid = session.get(Bid, bid_id)
    assert bid is not None
    bid.status = status
    session.commit()
    session.close()


def test_approval_roles_transitions_and_separation_of_duties(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    _set_status(bid_id, "waiting_tech_approval")
    tech = client.post(f"/api/bids/{bid_id}/approvals/tech", json={"decision": "approved"}, headers={"X-Actor": "developer"})
    assert tech.status_code == 200
    price = client.post(f"/api/bids/{bid_id}/approvals/price", json={"decision": "approved"}, headers={"X-Actor": "Nhu"})
    assert price.status_code == 200


def test_price_approval_locks_bid(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    _set_status(bid_id, "waiting_price_approval")
    response = client.post(f"/api/bids/{bid_id}/approvals/price", json={"decision": "approved", "comment": "Đã duyệt"}, headers={"X-Actor": "manager"})
    assert response.status_code == 200
    assert response.json()["status"] == "price_approved"
    assert response.json()["locked"] is True
