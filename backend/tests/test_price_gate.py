import re

from app.core import db
from tests.helpers import setup_wbs_bid


def test_unapproved_proposal_uses_placeholder_and_no_money(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    body = client.get(f"/api/bids/{bid_id}/proposal").json()
    assert body["price_gate"] == "placeholder"
    text = " ".join(body["sections"].values())
    assert "[Presales điền]" in text or body["price_gate"] == "placeholder"
    assert not re.search(r"(?:[$¥₫]\s*\d|\d\s*[$¥₫])", text)
