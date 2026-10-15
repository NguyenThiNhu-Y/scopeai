import math

from app.core import db
from app.models import Bid, Quotation
from tests.helpers import setup_wbs_bid


def test_pricing_uses_code_rate_overhead_contingency_and_trace(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    response = client.get(f"/api/bids/{bid_id}/quotation")
    assert response.status_code == 200
    body = response.json()
    assert body["contract_model"] == "fixed_price"
    assert body["totals"]["by_role"]
    assert body["totals"]["contingency_amount"] > 0
    assert body["trace"]["formula"]
    assert body["trace"]["reference_snapshot_id"]


def test_pricing_requires_wbs(client):
    response = client.post("/api/bids", json={
        "project_name": "Giả lập pricing",
        "customer_name": "Khách giả lập",
        "submission_deadline": "2026-12-15",
        "customer_language": "vi",
        "request_content": "Phạm vi giả lập đủ dài để vượt qua validation tối thiểu",
    })
    assert response.status_code == 201
    response = client.get(f"/api/bids/{response.json()['id']}/quotation")
    assert response.status_code == 409


def test_bid_list_uses_latest_computed_quotation_total(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    quotation = client.get(f"/api/bids/{bid_id}/quotation")
    assert quotation.status_code == 200
    expected = quotation.json()

    response = client.get("/api/bids")
    assert response.status_code == 200
    item = next(item for item in response.json()["items"] if item["id"] == bid_id)
    assert item["total_price"] == expected["totals"]["grand_total"]
    assert item["total_price_currency"] == expected["currency"]


def test_pricing_converts_budget_and_uses_display_currency(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal(), customer_language="ja")
    session = db.SessionLocal()
    bid = session.get(Bid, bid_id)
    bid.display_currency = "JPY"
    bid.budget_amount = 50000
    bid.budget_currency = "JPY"
    session.commit()
    session.close()
    body = client.get(f"/api/bids/{bid_id}/quotation").json()
    assert body["currency"] == "JPY"
    assert body["fx_rate"]["pair"] == "VND/JPY"
    assert body["budget"]["currency"] == "JPY"
    assert body["budget"]["difference"] is not None


def test_quotation_exposes_payment_milestones_from_schedule(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    from tests.helpers import put_schedule

    milestones = [{"name": "Kickoff", "percent": 20, "due_offset_days": 0}]
    put_schedule(client, bid_id, payment_milestones=milestones)

    body = client.get(f"/api/bids/{bid_id}/quotation").json()

    assert body["payment_milestones"][0]["name"] == "Kickoff"
    assert body["payment_milestones"][0]["percent"] == 20
    assert body["payment_milestones"][0]["due_offset_days"] == 0
    assert body["payment_milestones"][0]["due_date"] == "2026-11-01"


def test_quotation_includes_phase_man_days_and_budget_percentage(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal(), customer_language="ja")
    session = db.SessionLocal()
    bid = session.get(Bid, bid_id)
    bid.display_currency = "JPY"
    bid.budget_amount = 50000
    bid.budget_currency = "JPY"
    session.commit()
    session.close()

    body = client.get(f"/api/bids/{bid_id}/quotation").json()

    assert body["totals"]["phase_man_days"]
    assert body["budget"]["scope"] == "bid_budget"
    assert body["budget"]["scope_label_vi"] == "Ngân sách khách"
    assert body["budget"]["difference_percent"] is not None


def test_budget_scope_poc_compares_poc_price_and_labels(client):
    """Ngân sách phạm vi PoC: đối chiếu giá PoC (không dùng tổng dự án),
    hiển thị "Ngân sách PoC"."""
    bid_id = setup_wbs_bid(client, db.SessionLocal(), customer_language="ja")
    session = db.SessionLocal()
    bid = session.get(Bid, bid_id)
    bid.display_currency = "JPY"
    bid.budget_amount = 999999
    bid.budget_currency = "JPY"
    bid.budget_scope = "poc"
    session.commit()
    session.close()

    body = client.get(f"/api/bids/{bid_id}/quotation").json()
    budget = body["budget"]
    poc_price = body["totals"]["by_phase"]["poc"]

    assert budget["scope"] == "poc"
    assert budget["scope_label_vi"] == "Ngân sách PoC"
    # Chênh lệch tính theo giá PoC, không phải tổng dự án.
    assert budget["difference"] == round(poc_price - 999999, 2)
    assert budget["difference"] != round(body["totals"]["grand_total"] - 999999, 2)


def test_budget_warning_and_suggestion_are_bounded(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal(), customer_language="ja")
    session = db.SessionLocal()
    bid = session.get(Bid, bid_id)
    bid.display_currency = "JPY"
    bid.budget_amount = 50000
    bid.budget_currency = "JPY"
    session.commit()
    session.close()

    budget = client.get(f"/api/bids/{bid_id}/quotation").json()["budget"]
    assert abs(budget["adjustment_suggestion_percent"]) <= 30
    assert budget["scope_check_required"] is True
    assert "kiểm tra lại phạm vi/effort" in budget["warning"]


def test_quotation_settings_recalculate_with_validated_values(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal(), customer_language="ja")

    response = client.put(
        f"/api/bids/{bid_id}/quotation",
        json={
            "contract_model": "tm",
            "currency": "JPY",
            "contingency_percent": 12,
            "onsite_percent": 0.2,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["contract_model"] == "tm"
    assert body["currency"] == "JPY"
    assert body["contingency_percent"] == 12
    assert body["totals"]["onsite_percent"] == 0.2


def test_quotation_settings_reject_invalid_values(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())

    response = client.put(
        f"/api/bids/{bid_id}/quotation",
        json={"currency": "GBP", "onsite_percent": 1.1},
    )

    assert response.status_code == 400


def test_schedule_exposes_phase_role_work_breakdown(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal(), customer_language="ja")
    from tests.helpers import put_schedule

    response = put_schedule(client, bid_id)

    breakdown = response["work_breakdown"]
    assert breakdown
    assert set(breakdown) >= {"poc", "mvp", "production"}
    for phase in breakdown.values():
        # Tổng bằng tổng các vai trò (sai số float khi cộng nhiều số thập phân).
        assert math.isclose(
            phase["total"],
            sum(value for key, value in phase.items() if key != "total"),
            rel_tol=1e-9,
        )
