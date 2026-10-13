from app.core import db
from tests.helpers import setup_wbs_bid


def test_mitsumorisho_has_validity_tax_breakdown_and_rounding(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal(), customer_language="ja")
    session = db.SessionLocal()
    bid = session.get(__import__("app.models", fromlist=["Bid"]).Bid, bid_id)
    assert bid is not None
    bid.display_currency = "JPY"
    session.commit()
    session.close()
    body = client.get(f"/api/bids/{bid_id}/quotation").json()
    assert body["valid_until"]
    assert body["tax_mode"] == "tax_excluded"
    assert "by_role" in body["totals"]
    assert body["currency"] == "JPY"
    assert body["totals"]["grand_total"] % 1 == 0
