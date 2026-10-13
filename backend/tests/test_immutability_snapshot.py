from app.core import db
from app.models import Quotation
from tests.helpers import setup_wbs_bid


def test_quotation_keeps_reference_snapshot(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    first = client.get(f"/api/bids/{bid_id}/quotation")
    assert first.status_code == 200
    session = db.SessionLocal()
    row = session.query(Quotation).filter_by(bid_id=bid_id).first()
    assert row is not None
    snapshot_id = row.reference_snapshot_id
    session.close()
    second = client.get(f"/api/bids/{bid_id}/quotation")
    assert second.status_code == 200
    assert second.json()["trace"]["reference_snapshot_id"] == snapshot_id
    assert second.json()["totals"] == first.json()["totals"]
