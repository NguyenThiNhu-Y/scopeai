"""Test độ tin cậy từng hồ sơ — thiet_ke_danh_gia.md §5.

Mỗi tín hiệu: pass/warn/fail/na đúng ngưỡng (confidence.yaml); quy tắc ra mức
Thấp/Trung bình/Cao (§5.3); điểm tương đồng (§5.4); history_bias.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from app.services.confidence_engine import (
    compute_confidence,
    decide_level,
    find_similar_cases,
    history_bias,
    keyword_overlap,
    similarity_score,
)

_THRESHOLDS = yaml.safe_load(
    (Path(__file__).resolve().parents[1] / "app" / "reference" / "confidence.yaml").read_text()
)

_RAG_CASE = {
    "id": "cs_rag_a",
    "title": "Case RAG bảo trì (giả lập)",
    "industry": "Sản xuất",
    "market": "jp",
    "customer_language": "ja",
    "direction": "rag",
    "requirement_count": 30,
    "estimated_man_day": {"poc": 30, "mvp": 120, "production": 60},
    "actual_man_day": {"poc": 31, "mvp": 142, "production": 62},
}

_RAG_CASE_B = {
    **_RAG_CASE,
    "id": "cs_rag_b",
    "requirement_count": 40,
    "actual_man_day": {"poc": 35, "mvp": 150, "production": 70},
}

_NONE_CASE = {
    "id": "cs_none_a",
    "title": "Case CRM (giả lập)",
    "industry": "Dịch vụ",
    "market": "vn",
    "customer_language": "vi",
    "direction": "none",
    "requirement_count": 20,
    "estimated_man_day": {"poc": 20, "mvp": 80, "production": 40},
    "actual_man_day": {"poc": 22, "mvp": 90, "production": 45},
}


def _base_data(**overrides) -> dict:
    data = {
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
        "requirements": {"total": 30, "covered": 29, "uncovered": ["FR-019"]},
        "evaluations": {"uncertain": 2, "total": 30},
        "wbs_check": {
            "pm_qa_ok": True,
            "within_20pct": True,
            "cycle_free": True,
            "leaf_within_limit": True,
        },
        "wbs_total": 570.0,
        "effort": {"midpoint_total": 555.0, "by_phase": {}},
        "schedule": {
            "earliest_mvp_start": "2027-03-01",
            "earliest_production_start": "2027-06-15",
            "go_no_go_end": "2027-02-20",
            "end_date": "2027-09-20",
            "warning": None,
        },
        "case_studies": [_RAG_CASE, _RAG_CASE_B],
    }
    data.update(overrides)
    return data


def _signal(result: dict, key: str) -> dict:
    return next(s for s in result["signals"] if s["key"] == key)


# ---------------------------------------------------------------- input_completeness

def test_input_completeness_pass_warn_fail():
    result = compute_confidence(_base_data(), _THRESHOLDS)
    assert _signal(result, "input_completeness")["status"] == "pass"

    bid = _base_data()["bid"]
    bid["budget_amount"] = None
    result = compute_confidence(_base_data(bid=bid), _THRESHOLDS)
    assert _signal(result, "input_completeness")["status"] == "warn"

    bid = _base_data()["bid"]
    bid["budget_amount"] = None
    bid["customer_schedule_start"] = None
    bid["customer_mvp_start"] = None
    bid["customer_production_start"] = None
    result = compute_confidence(_base_data(bid=bid), _THRESHOLDS)
    assert _signal(result, "input_completeness")["status"] == "fail"

    result = compute_confidence(
        _base_data(questions={"blocking_unanswered": 1}), _THRESHOLDS
    )
    assert _signal(result, "input_completeness")["status"] == "fail"


# ---------------------------------------------------------------- wbs_checks

def test_wbs_checks_pass_fail_na():
    result = compute_confidence(_base_data(), _THRESHOLDS)
    assert _signal(result, "wbs_checks")["status"] == "pass"

    check = _base_data()["wbs_check"]
    check["cycle_free"] = False
    result = compute_confidence(_base_data(wbs_check=check), _THRESHOLDS)
    assert _signal(result, "wbs_checks")["status"] == "fail"

    result = compute_confidence(_base_data(wbs_check=None), _THRESHOLDS)
    assert _signal(result, "wbs_checks")["status"] == "na"


# ---------------------------------------------------------------- schedule_checks

def test_schedule_checks_pass_warn_fail_na():
    result = compute_confidence(_base_data(), _THRESHOLDS)
    assert _signal(result, "schedule_checks")["status"] == "pass"

    schedule = _base_data()["schedule"]
    schedule["end_date"] = "2027-10-05"  # trễ 5 ngày so mốc 2027-09-30
    result = compute_confidence(_base_data(schedule=schedule), _THRESHOLDS)
    assert _signal(result, "schedule_checks")["status"] == "warn"

    schedule = _base_data()["schedule"]
    schedule["end_date"] = "2027-10-20"  # trễ 20 ngày > 14
    result = compute_confidence(_base_data(schedule=schedule), _THRESHOLDS)
    assert _signal(result, "schedule_checks")["status"] == "fail"

    schedule = _base_data()["schedule"]
    schedule["earliest_mvp_start"] = "2027-02-01"  # trước go_no_go_end 2027-02-20
    result = compute_confidence(_base_data(schedule=schedule), _THRESHOLDS)
    assert _signal(result, "schedule_checks")["status"] == "fail"

    result = compute_confidence(_base_data(schedule=None), _THRESHOLDS)
    assert _signal(result, "schedule_checks")["status"] == "na"

    # Khách không nêu ngày kết thúc (Phase mở "2027年10月〜") → không so ngày kết thúc.​
    bid = _base_data()["bid"]
    bid["customer_schedule_end"] = None
    schedule = _base_data()["schedule"]
    schedule["end_date"] = "2027-12-31"  # trễ nhưng không có mốc khách để so
    result = compute_confidence(_base_data(bid=bid, schedule=schedule), _THRESHOLDS)

    assert _signal(result, "schedule_checks")["status"] == "pass"


# ---------------------------------------------------------------- traceability

def test_traceability_pass_warn_fail_na():
    result = compute_confidence(_base_data(), _THRESHOLDS)
    assert _signal(result, "traceability")["status"] == "pass"  # 29/30 = 96.7%

    result = compute_confidence(
        _base_data(requirements={"total": 30, "covered": 26, "uncovered": []}), _THRESHOLDS
    )
    assert _signal(result, "traceability")["status"] == "warn"  # 86.7%

    result = compute_confidence(
        _base_data(requirements={"total": 30, "covered": 20, "uncovered": []}), _THRESHOLDS
    )
    assert _signal(result, "traceability")["status"] == "fail"  # 66.7%

    result = compute_confidence(
        _base_data(requirements={"total": 0, "covered": 0, "uncovered": []}), _THRESHOLDS
    )
    assert _signal(result, "traceability")["status"] == "na"


# ---------------------------------------------------------------- coverage_uncertainty

def test_coverage_uncertainty_pass_warn_fail_na():
    result = compute_confidence(_base_data(), _THRESHOLDS)
    assert _signal(result, "coverage_uncertainty")["status"] == "pass"  # 2/30 = 6.7%

    result = compute_confidence(
        _base_data(evaluations={"uncertain": 6, "total": 30}), _THRESHOLDS
    )
    assert _signal(result, "coverage_uncertainty")["status"] == "warn"  # 20%

    result = compute_confidence(
        _base_data(evaluations={"uncertain": 12, "total": 30}), _THRESHOLDS
    )
    assert _signal(result, "coverage_uncertainty")["status"] == "fail"  # 40%

    result = compute_confidence(
        _base_data(evaluations={"uncertain": 0, "total": 0}), _THRESHOLDS
    )
    assert _signal(result, "coverage_uncertainty")["status"] == "na"


# ---------------------------------------------------------------- analog

def test_analog_pass_warn_fail_na():
    # 2 case rag: actual 235 và 255 → khoảng mở rộng ±10% = [211.5, 280.5].
    result = compute_confidence(_base_data(wbs_total=240.0), _THRESHOLDS)
    assert _signal(result, "analog")["status"] == "pass"
    assert _signal(result, "analog")["data"]["position"] == "inside"

    result = compute_confidence(_base_data(wbs_total=300.0), _THRESHOLDS)
    signal = _signal(result, "analog")
    assert signal["status"] == "warn"  # lệch ~7% ≤ 20%
    assert signal["data"]["position"] == "above"

    result = compute_confidence(_base_data(wbs_total=400.0), _THRESHOLDS)
    assert _signal(result, "analog")["status"] == "fail"
    assert _signal(result, "analog")["data"]["position"] == "above"

    result = compute_confidence(
        _base_data(case_studies=[_RAG_CASE]), _THRESHOLDS
    )
    signal = _signal(result, "analog")
    assert signal["status"] == "na"
    assert signal["data"]["position"] == "insufficient"


# ---------------------------------------------------------------- history_bias

def test_history_bias_pass_warn_na():
    # cs_rag_a: 235/210 = 1.119; cs_rag_b: 255/230 = 1.109 → median 1.114 → warn.
    result = compute_confidence(_base_data(), _THRESHOLDS)
    signal = _signal(result, "history_bias")
    assert signal["status"] == "warn"
    assert signal["data"]["case_count"] == 2
    assert signal["data"]["direction"] == "above"

    cases = [
        {**_RAG_CASE, "estimated_man_day": {"poc": 31, "mvp": 142, "production": 62}},
        {**_RAG_CASE_B, "estimated_man_day": {"poc": 35, "mvp": 150, "production": 70}},
    ]
    result = compute_confidence(_base_data(case_studies=cases), _THRESHOLDS)
    assert _signal(result, "history_bias")["status"] == "pass"  # median ≈ 1.0

    result = compute_confidence(_base_data(case_studies=[_RAG_CASE]), _THRESHOLDS)
    assert _signal(result, "history_bias")["status"] == "na"


# ---------------------------------------------------------------- quy tắc ra mức (§5.3)

def test_level_low_when_important_signal_fails():
    check = _base_data()["wbs_check"]
    check["pm_qa_ok"] = False
    result = compute_confidence(_base_data(wbs_check=check), _THRESHOLDS)
    assert result["level"] == "low"
    assert result["level_label_vi"] == "Thấp"


def test_level_low_when_two_fails():
    data = _base_data(
        evaluations={"uncertain": 12, "total": 30},  # fail
        requirements={"total": 30, "covered": 20, "uncovered": []},  # fail (quan trọng)
    )
    result = compute_confidence(data, _THRESHOLDS)
    assert result["level"] == "low"


def test_level_medium_when_one_nonimportant_fail():
    # Chỉ coverage_uncertainty fail (12/30 = 40%); analog pass (wbs_total 240 trong khoảng).
    data = _base_data(
        evaluations={"uncertain": 12, "total": 30},
        wbs_total=240.0,
    )
    result = compute_confidence(data, _THRESHOLDS)
    assert result["level"] == "medium"


def test_level_medium_when_two_warns():
    data = _base_data(
        requirements={"total": 30, "covered": 26, "uncovered": []},  # warn
        evaluations={"uncertain": 6, "total": 30},  # warn
        wbs_total=240.0,
    )
    result = compute_confidence(data, _THRESHOLDS)
    assert result["level"] == "medium"


def test_level_high_when_all_pass_or_na():
    data = _base_data(
        requirements={"total": 30, "covered": 29, "uncovered": []},
        evaluations={"uncertain": 2, "total": 30},
        case_studies=[_RAG_CASE],  # analog + history_bias → na
        wbs_total=240.0,
    )
    result = compute_confidence(data, _THRESHOLDS)
    assert result["level"] == "high"


def test_summary_vi_lists_fail_before_warn_max_three():
    data = _base_data(
        requirements={"total": 30, "covered": 20, "uncovered": []},  # fail
        evaluations={"uncertain": 6, "total": 30},  # warn
        questions={"blocking_unanswered": 1},  # fail
        wbs_total=240.0,
    )
    result = compute_confidence(data, _THRESHOLDS)
    summary = result["summary_vi"]
    fail_index = summary.find("Truy vết requirement")
    warn_index = summary.find("Độ chắc")
    assert fail_index != -1 and warn_index != -1
    assert fail_index < warn_index
    assert summary.count("; ") <= 2  # tối đa 3 lý do


# ---------------------------------------------------------------- tương đồng (§5.4)

def test_similarity_score_formula():
    weights = _THRESHOLDS["thresholds"]["similarity"]["weights"]
    score = similarity_score(
        _RAG_CASE,
        market="jp",
        customer_language="ja",
        requirement_count=30,
        summary_keywords=set(),
        weights=weights,
    )
    # 0.4*1 + 0.3*1 + 0.2*1 + 0.1*0 = 0.9
    assert abs(score - 0.9) < 1e-9

    score = similarity_score(
        _RAG_CASE,
        market="vn",
        customer_language="vi",
        requirement_count=30,
        summary_keywords=set(),
        weights=weights,
    )
    # 0.4*0 + 0.3*1 + 0.2*0 + 0.1*0 = 0.3
    assert abs(score - 0.3) < 1e-9


def test_keyword_overlap():
    case = {"title": "Case RAG bảo trì (giả lập)", "industry": "Sản xuất"}
    assert keyword_overlap(case, {"bảo", "trì", "sản", "xuất"}) > 0
    assert keyword_overlap(case, {"không", "liên", "quan"}) == 0.0


def test_find_similar_cases_filters_by_direction_and_actual():
    cases = [_RAG_CASE, _RAG_CASE_B, _NONE_CASE]
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
    assert "cs_none_a" not in ids
    assert len(similar) <= 3
    similarities = [case["similarity"] for case in similar]
    assert similarities == sorted(similarities, reverse=True)


def test_history_bias_function():
    bias = history_bias([_RAG_CASE, _RAG_CASE_B], "rag", _THRESHOLDS)
    assert bias is not None
    assert bias["case_count"] == 2
    assert bias["direction"] == "above"
    assert bias["median_actual_over_estimate"] > 1.0

    assert history_bias([_RAG_CASE], "rag", _THRESHOLDS) is None
    assert history_bias([_RAG_CASE, _RAG_CASE_B], "none", _THRESHOLDS) is None


def test_decide_level_direct():
    signals = [
        {"key": "wbs_checks", "status": "fail", "label_vi": "Kiểm tra WBS", "detail_vi": "x"},
    ]
    assert decide_level(signals, _THRESHOLDS)["level"] == "low"
    signals = [
        {"key": "analog", "status": "fail", "label_vi": "So với dự án tương tự", "detail_vi": "x"},
    ]
    assert decide_level(signals, _THRESHOLDS)["level"] == "medium"
    signals = [
        {"key": "analog", "status": "warn", "label_vi": "So với dự án tương tự", "detail_vi": "x"},
        {"key": "history_bias", "status": "warn", "label_vi": "Sai lệch lịch sử", "detail_vi": "x"},
    ]
    assert decide_level(signals, _THRESHOLDS)["level"] == "medium"
    signals = [
        {"key": "analog", "status": "pass", "label_vi": "So với dự án tương tự", "detail_vi": "x"},
    ]
    assert decide_level(signals, _THRESHOLDS)["level"] == "high"