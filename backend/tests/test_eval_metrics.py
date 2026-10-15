"""Unit test metrics.py — thiet_ke_danh_gia.md §6.2."""

from __future__ import annotations

from eval.metrics import (
    aggregate_metrics,
    actual_total_for_expected,
    checks_pass,
    compute_metrics,
    direction_ok,
    duration_weeks_error,
    expected_total_range,
    interval_hit,
    must_trace_ok,
    phase_share_error,
    stability_cv,
    total_ape,
    total_in_expected,
    traceability_pct,
)

_EXPECTED = {
    "acceptable_directions": ["none"],
    "total_man_day": [220, 270],
    "phase_man_day": {"poc": [28, 38], "mvp": [130, 170], "production": [55, 75]},
    "duration_weeks": [24, 30],
    "must_trace": ["FR-001", "NFR-003"],
}


def test_direction_ok():
    assert direction_ok("none", ["none"]) is True
    assert direction_ok("rag", ["none"]) is False
    assert direction_ok(None, ["none"]) is False


def test_expected_total_range():
    assert expected_total_range(_EXPECTED) == [220.0, 270.0]
    partial = {"phase_man_day": {"poc": [60, 90]}}
    assert expected_total_range(partial) == [60.0, 90.0]
    assert expected_total_range({}) is None


def test_actual_total_for_expected_partial():
    by_phase = {"poc": 75.0, "mvp": 400.0, "production": 150.0}
    # Chỉ chấm PoC (case tokai) → tổng = 75, không cộng MVP/Production.
    assert actual_total_for_expected(by_phase, {"phase_man_day": {"poc": [60, 90]}}) == 75.0
    assert actual_total_for_expected(by_phase, _EXPECTED) == 625.0


def test_total_ape():
    assert total_ape(245.0, [220, 270]) == 0.0  # đúng trung điểm 245
    assert abs(total_ape(280.0, [220, 270]) - 14.3) < 0.1
    assert total_ape(100.0, None) is None


def test_total_in_expected():
    assert total_in_expected(240.0, [220, 270]) is True
    assert total_in_expected(300.0, [220, 270]) is False
    assert total_in_expected(240.0, None) is False


def test_interval_hit():
    assert interval_hit({"min": 200, "max": 260}, [220, 270]) is True
    assert interval_hit({"min": 280, "max": 320}, [220, 270]) is False
    assert interval_hit(None, [220, 270]) is False


def test_phase_share_error():
    # Đáp án: poc 33, mvp 150, production 65 → tổng 248.
    # Ước lượng: poc 40, mvp 140, production 60 → tổng 240.
    actual = {"poc": 40.0, "mvp": 140.0, "production": 60.0}
    error = phase_share_error(actual, _EXPECTED)
    assert error is not None and 0.0 <= error <= 1.0
    # Giống hệt đáp án → 0.
    exact = {"poc": 33.0, "mvp": 150.0, "production": 65.0}
    assert phase_share_error(exact, _EXPECTED) == 0.0
    assert phase_share_error({}, {}) is None


def test_traceability_pct():
    assert traceability_pct(34, 36) == 94.4
    assert traceability_pct(0, 0) is None


def test_must_trace_ok():
    assert must_trace_ok({"FR-001", "FR-009", "NFR-003"}, ["FR-001", "NFR-003"]) is True
    assert must_trace_ok({"FR-001"}, ["FR-001", "NFR-003"]) is False


def test_checks_pass():
    flags = {"pm_qa_ok": True, "within_20pct": True, "cycle_free": True, "leaf_within_limit": True}
    assert checks_pass(flags, True) == 1.0
    assert checks_pass(flags, False) == 0.8
    assert checks_pass(flags, None) == 1.0
    flags["cycle_free"] = False
    assert checks_pass(flags, None) == 0.75


def test_duration_weeks_error():
    assert duration_weeks_error(27.0, _EXPECTED) == 0.0  # trung điểm 27
    assert duration_weeks_error(30.0, _EXPECTED) == 3.0
    assert duration_weeks_error(None, _EXPECTED) is None
    # Case chỉ chấm PoC: dùng poc_duration_weeks.
    tokai = {"poc_duration_weeks": [10, 13]}
    assert duration_weeks_error(11.5, tokai) == 0.0


def test_stability_cv():
    assert stability_cv([100.0]) is None
    cv = stability_cv([100.0, 110.0])
    assert cv is not None and cv > 0


def test_compute_metrics_full():
    run = {
        "direction": "none",
        "wbs_total": 248.0,
        "wbs_by_phase": {"poc": 33.0, "mvp": 150.0, "production": 65.0},  # tổng 248
        "effort_range": {"min": 200.0, "max": 260.0},
        "traceability": {"covered": 34, "total": 36, "covered_codes": {"FR-001", "NFR-003"}},
        "wbs_checks": {
            "pm_qa_ok": True,
            "within_20pct": True,
            "cycle_free": True,
            "leaf_within_limit": True,
        },
        "schedule_ok": True,
        "duration_weeks": 27.0,
        "question_rounds": 1,
        "question_count": 3,
        "confidence_level": "medium",
        "llm_calls": 6,
        "seconds": 1.2,
        "wbs_totals_across_repeats": [245.0],
    }
    metrics = compute_metrics(run, _EXPECTED)
    assert metrics["direction_ok"] is True
    assert abs(metrics["total_ape"] - 1.2) < 0.1  # |248−245|/245
    assert metrics["total_in_expected"] is True
    assert metrics["interval_hit"] is True
    assert metrics["phase_share_error"] == 0.0
    assert metrics["traceability_pct"] == 94.4
    assert metrics["must_trace_ok"] is True
    assert metrics["checks_pass"] == 1.0
    assert metrics["duration_weeks_error"] == 0.0
    assert metrics["question_rounds"] == 1
    assert metrics["question_count"] == 3
    assert metrics["confidence_level"] == "medium"
    assert metrics["llm_calls"] == 6
    assert metrics["seconds"] == 1.2


def test_aggregate_metrics():
    base = {
        "direction_ok": True,
        "total_ape": 10.0,
        "total_in_expected": True,
        "interval_hit": True,
        "traceability_pct": 90.0,
        "checks_pass": 0.8,
        "question_rounds": 1,
        "question_count": 2,
        "llm_calls": 5,
        "seconds": 1.0,
    }
    second = dict(base)
    second["total_ape"] = 20.0
    second["total_in_expected"] = False
    second["interval_hit"] = False
    second["direction_ok"] = False
    summary = aggregate_metrics([base, second])
    assert summary["case_count"] == 2
    assert summary["mape"] == 15.0
    assert summary["total_in_expected_rate"] == 0.5
    assert summary["interval_hit_rate"] == 0.5
    assert summary["direction_ok_pct"] == 50.0
    assert summary["avg_traceability_pct"] == 90.0
    assert summary["checks_pass_pct"] == 80.0
    assert summary["avg_llm_calls"] == 5.0
    assert aggregate_metrics([]) == {}