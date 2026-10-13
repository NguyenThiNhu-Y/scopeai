from datetime import date

from app.core import db
from app.models import Bid
from tests.helpers import default_team_allocation, put_schedule, setup_wbs_bid


def test_tm_and_odc_payment_rows_include_code_computed_values(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal(), customer_language="ja")
    tm = client.put(
        f"/api/bids/{bid_id}/quotation",
        json={"contract_model": "tm", "currency": "JPY", "tm_months": 3},
    ).json()
    assert len(tm["totals"]["payment_plan"]) == 3
    assert all(row["amount"] > 0 for row in tm["totals"]["payment_plan"])

    odc = client.put(
        f"/api/bids/{bid_id}/quotation",
        json={"contract_model": "odc", "currency": "JPY", "odc_fte": 2, "odc_months": 4},
    ).json()
    assert odc["totals"]["odc_fte_months"] == 8
    assert all(row["fte_months"] == 8 for row in odc["totals"]["payment_plan"])


def test_intake_schedule_dates_are_exposed_in_bid_and_schedule(client):
    response = client.post(
        "/api/bids",
        json={
            "project_name": "Lịch CRM giả lập",
            "customer_name": "Khách Nhật giả lập",
            "submission_deadline": "2026-12-15",
            "customer_language": "ja",
            "request_content": "2027年1月着手、6月MVP、9月本番のCRM giả lập đủ dài.",
            "customer_mvp_start": "2027-06-01",
            "customer_production_start": "2027-09-01",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["customer_mvp_start"] == "2027-06-01"
    assert body["customer_production_start"] == "2027-09-01"


def test_schedule_uses_explicit_customer_phase_dates(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal(), customer_language="ja")
    session = db.SessionLocal()
    bid = session.get(Bid, bid_id)
    assert bid is not None
    bid.customer_mvp_start = date(2027, 6, 1)
    bid.customer_production_start = date(2027, 9, 1)
    session.commit()
    session.close()
    schedule = put_schedule(client, bid_id)
    assert schedule["customer_mvp_start"] == "2027-06-01"
    assert schedule["customer_production_start"] == "2027-09-01"


def test_schedule_exposes_go_no_go_break_interval(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal(), customer_language="ja")
    schedule = put_schedule(client, bid_id)
    assert schedule["go_no_go_gap_working_days"] == 10
    assert schedule["go_no_go_start"]
    assert schedule["go_no_go_end"]
