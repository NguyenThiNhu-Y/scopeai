"""Test tìm case tương tự + tín hiệu analog — thiet_ke_danh_gia.md §5.4.

- Điểm tương đồng 0–1 theo công thức cố định (không nhân hệ số, không quy đổi quy mô).
- Lọc: cùng direction + có actual_man_day; tối đa 3 case điểm ≥ 0,5 giảm dần.
- Dưới 2 case → position = insufficient (tín hiệu na).
- Endpoint GET /bids/{id}/confidence trả đúng ConfidenceOut.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from app.services.confidence_engine import (
    compute_confidence,
    find_similar_cases,
    similarity_score,
)

_THRESHOLDS = yaml.safe_load(
    (Path(__file__).resolve().parents[1] / "app" / "reference" / "confidence.yaml").read_text()
)

_CASE_TEMPLATE = {
    "id": "cs_tpl",
    "title": "Case mẫu (giả lập)",
    "industry": "Sản xuất",
    "market": "jp",
    "customer_language": "ja",
    "direction": "rag",
    "requirement_count": 30,
    "estimated_man_day": {"poc": 30, "mvp": 120, "production": 60},
    "actual_man_day": {"poc": 31, "mvp": 142, "production": 62},
}


def _case(case_id: str, **overrides) -> dict:
    case = dict(_CASE_TEMPLATE)
    case["id"] = case_id
    case.update(overrides)
    return case


def _data(case_studies: list[dict], wbs_total: float | None = 580.0) -> dict:
    return {
        "bid": {
            "market": "jp",
            "budget_amount": 15000000,
            "customer_schedule_start": "2026-12-01",
            "customer_mvp_start": "2027-06-01",
            "customer_production_start": "2027-09-01",
            "customer_schedule_end": "2027-09-30",
            "customer_language": "ja",
            "no_requirement_file": False,
            "request_content": "Hệ thống bảo trì máy móc dùng RAG truy vấn tài liệu kỹ thuật tiếng Nhật.",
        },
        "direction": "rag",
        "questions": {"blocking_unanswered": 0},
        "requirements": {"total": 30, "covered": 29, "uncovered": []},
        "evaluations": {"uncertain": 2, "total": 30},
        "wbs_check": {
            "pm_qa_ok": True,
            "within_20pct": True,
            "cycle_free": True,
            "leaf_within_limit": True,
        },
        "wbs_total": wbs_total,
        "effort": {"midpoint_total": 565.0, "by_phase": {}},
        "schedule": {
            "earliest_mvp_start": "2027-03-01",
            "earliest_production_start": "2027-06-15",
            "go_no_go_end": "2027-02-20",
            "end_date": "2027-09-20",
            "warning": None,
        },
        "case_studies": case_studies,
    }


def test_similarity_requires_same_direction_and_actual():
    cases = [
        _case("cs_rag_1", direction="rag", actual_man_day={"poc": 1, "mvp": 2, "production": 3}),
        _case("cs_none_1", direction="none", actual_man_day={"poc": 1, "mvp": 2, "production": 3}),
        _case("cs_rag_lost", direction="rag", actual_man_day=None),
    ]
    similar = find_similar_cases(
        cases,
        direction="rag",
        market="jp",
        customer_language="ja",
        requirement_count=30,
        summary_keywords=set(),
        thresholds=_THRESHOLDS,
    )
    ids = [case["id"] for case in similar]
    assert ids == ["cs_rag_1"]
    assert "cs_none_1" not in ids
    assert "cs_rag_lost" not in ids


def test_similarity_scores_descending_and_capped_at_three():
    cases = [
        _case("cs_a", requirement_count=30),
        _case("cs_b", requirement_count=35),
        _case("cs_c", requirement_count=40),
        _case("cs_d", requirement_count=100),
    ]
    similar = find_similar_cases(
        cases,
        direction="rag",
        market="jp",
        customer_language="ja",
        requirement_count=30,
        summary_keywords=set(),
        thresholds=_THRESHOLDS,
    )
    assert len(similar) <= 3
    scores = [case["similarity"] for case in similar]
    assert scores == sorted(scores, reverse=True)
    # cs_d lệch requirement quá → điểm < 0,5 → bị loại.
    assert "cs_d" not in [case["id"] for case in similar]


def test_similarity_score_never_scaled_by_size():
    """Không quy đổi quy mô: case ít requirement vẫn tính theo công thức gốc."""
    weights = _THRESHOLDS["thresholds"]["similarity"]["weights"]
    small = _case("cs_small", requirement_count=10)
    score = similarity_score(
        small,
        market="jp",
        customer_language="ja",
        requirement_count=30,
        summary_keywords=set(),
        weights=weights,
    )
    # 0.4 + 0.3*(1 - 20/30) + 0.2 + 0 = 0.7
    assert abs(score - 0.7) < 1e-9


def test_position_insufficient_when_less_than_two_cases():
    result = compute_confidence(_data([_case("cs_only")]), _THRESHOLDS)
    analog = result["analog"]
    assert analog["position"] == "insufficient"
    assert analog["actual_total_range"] == []
    signal = next(s for s in result["signals"] if s["key"] == "analog")
    assert signal["status"] == "na"
    assert "Chưa đủ dữ liệu tham chiếu" in signal["detail_vi"]


def test_position_below_inside_above():
    cases = [
        _case("cs_lo", actual_man_day={"poc": 30, "mvp": 100, "production": 50}),  # 180
        _case("cs_hi", actual_man_day={"poc": 40, "mvp": 130, "production": 60}),  # 230
    ]
    # Khoảng mở rộng ±10%: [162, 253].
    result = compute_confidence(_data(cases, wbs_total=200.0), _THRESHOLDS)
    assert result["analog"]["position"] == "inside"

    result = compute_confidence(_data(cases, wbs_total=100.0), _THRESHOLDS)
    assert result["analog"]["position"] == "below"

    result = compute_confidence(_data(cases, wbs_total=400.0), _THRESHOLDS)
    assert result["analog"]["position"] == "above"


def test_analog_range_and_cases_in_output():
    cases = [
        _case("cs_lo", actual_man_day={"poc": 30, "mvp": 100, "production": 50}),
        _case("cs_hi", actual_man_day={"poc": 40, "mvp": 130, "production": 60}),
    ]
    result = compute_confidence(_data(cases, wbs_total=200.0), _THRESHOLDS)
    analog = result["analog"]
    assert analog["actual_total_range"] == [180.0, 230.0]
    # Hai case cùng điểm tương đồng → xếp theo id (tie-break ổn định).
    assert [case["id"] for case in analog["cases"]] == ["cs_hi", "cs_lo"]
    assert analog["estimate_total"] == 200.0
    assert analog["effort_midpoint"] == 565.0
    # Case tương tự giữ số thực tế GỐC (không quy đổi quy mô).
    assert analog["cases"][0]["actual_man_day"]["mvp"] == 130.0
    assert analog["cases"][0]["actual_total"] == 230.0


def test_confidence_endpoint_shape(client):
    """GET /api/bids/{id}/confidence trả đúng cấu trúc ConfidenceOut."""
    from app.core import db
    from tests.helpers import setup_wbs_bid

    session = db.SessionLocal()
    try:
        bid_id = setup_wbs_bid(client, session, direction="rag")
    finally:
        session.close()
    resp = client.get(f"/api/bids/{bid_id}/confidence")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["level"] in ("high", "medium", "low")
    assert body["level_label_vi"] in ("Cao", "Trung bình", "Thấp")
    assert isinstance(body["summary_vi"], str)
    assert len(body["signals"]) == 7
    for signal in body["signals"]:
        assert signal["status"] in ("pass", "warn", "fail", "na")
        assert signal["label_vi"]
        assert signal["detail_vi"]
    assert body["analog"]["position"] in ("below", "inside", "above", "insufficient")
    assert isinstance(body["thresholds_version"], int)
    assert isinstance(body["case_studies_version"], int)