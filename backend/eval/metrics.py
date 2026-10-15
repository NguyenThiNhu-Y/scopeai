"""Chỉ số đánh giá offline — thiet_ke_danh_gia.md §6.2.

Hàm thuần: đầu vào là dict kết quả chạy pipeline + dict ``expected`` trong file
golden case; đầu ra là chỉ số. KHÔNG gọi LLM, KHÔNG đọc DB — có unit test riêng.

Quy ước case chỉ chấm một phần (vd gc_tokai_rag chỉ chấm PoC): mọi chỉ số dùng
các giai đoạn CÓ trong ``expected.phase_man_day`` (xem ``_expected_phases``).
"""

from __future__ import annotations

import math
import statistics
from typing import Any


def _expected_phases(expected: dict) -> list[str]:
    """Các giai đoạn được chấm = các phase có trong ``expected.phase_man_day``.

    Nếu expected có ``total_man_day`` thì chấm toàn bộ 3 giai đoạn.
    """
    phases = list((expected.get("phase_man_day") or {}).keys())
    if expected.get("total_man_day"):
        return ["poc", "mvp", "production"]
    return phases


def expected_total_range(expected: dict) -> list[float] | None:
    """Khoảng tổng man-day đáp án — tổng các phase được chấm nếu không có sẵn."""
    if expected.get("total_man_day"):
        return [float(v) for v in expected["total_man_day"]]
    phases = _expected_phases(expected)
    if not phases:
        return None
    lows = sum(expected["phase_man_day"][phase][0] for phase in phases)
    highs = sum(expected["phase_man_day"][phase][1] for phase in phases)
    return [lows, highs]


def actual_total_for_expected(wbs_by_phase: dict[str, float], expected: dict) -> float:
    """Tổng WBS chỉ tính trên các giai đoạn được chấm (tokai: chỉ PoC)."""
    phases = _expected_phases(expected)
    return round(sum(float(wbs_by_phase.get(phase) or 0.0) for phase in phases), 1)


def direction_ok(actual: str | None, acceptable: list[str]) -> bool:
    return actual in acceptable


def total_ape(actual_total: float, expected_range: list[float] | None) -> float | None:
    """|tổng WBS − trung điểm đáp án| ÷ trung điểm (%)."""
    if not expected_range or expected_range[0] + expected_range[1] <= 0:
        return None
    midpoint = (expected_range[0] + expected_range[1]) / 2
    return round(abs(actual_total - midpoint) / midpoint * 100, 1)


def total_in_expected(actual_total: float, expected_range: list[float] | None) -> bool:
    if not expected_range:
        return False
    return expected_range[0] <= actual_total <= expected_range[1]


def interval_hit(
    effort_range: dict[str, float] | None, expected_range: list[float] | None
) -> bool:
    """Khoảng [min, max] của effort engine giao với khoảng đáp án."""
    if not effort_range or not expected_range:
        return False
    return max(effort_range["min"], expected_range[0]) <= min(
        effort_range["max"], expected_range[1]
    )


def phase_share_error(
    actual_by_phase: dict[str, float], expected: dict
) -> float | None:
    """½ × Σ |tỉ trọng giai đoạn ước lượng − tỉ trọng đáp án| (0–1)."""
    phases = _expected_phases(expected)
    phase_expected = expected.get("phase_man_day") or {}
    if not phases or not phase_expected:
        return None
    expected_mids = {
        phase: (phase_expected[phase][0] + phase_expected[phase][1]) / 2
        for phase in phases
    }
    expected_sum = sum(expected_mids.values())
    actual_sum = sum(float(actual_by_phase.get(phase) or 0.0) for phase in phases)
    if expected_sum <= 0 or actual_sum <= 0:
        return None
    error = 0.0
    for phase in phases:
        share_expected = expected_mids[phase] / expected_sum
        share_actual = (float(actual_by_phase.get(phase) or 0.0)) / actual_sum
        error += abs(share_expected - share_actual)
    return round(0.5 * error, 3)


def traceability_pct(covered: int, total: int) -> float | None:
    if total <= 0:
        return None
    return round(covered / total * 100, 1)


def must_trace_ok(covered_codes: set[str], must_trace: list[str]) -> bool:
    return set(must_trace or []) <= set(covered_codes or [])


def checks_pass(wbs_flags: dict[str, bool], schedule_ok: bool | None) -> float:
    """Số kiểm tra WBS + lịch đạt / tổng (0–1); thiếu lịch → chỉ tính WBS."""
    flags = [bool(value) for value in (wbs_flags or {}).values()]
    if schedule_ok is not None:
        flags.append(bool(schedule_ok))
    if not flags:
        return 0.0
    return round(sum(flags) / len(flags), 3)


def duration_weeks_error(
    actual_weeks: float | None, expected: dict
) -> float | None:
    """|tổng tuần theo lịch − trung điểm tuần đáp án|."""
    if actual_weeks is None:
        return None
    if expected.get("duration_weeks"):
        low, high = expected["duration_weeks"]
    elif expected.get("poc_duration_weeks"):
        low, high = expected["poc_duration_weeks"]
    else:
        return None
    return round(abs(actual_weeks - (low + high) / 2), 1)


def stability_cv(values: list[float]) -> float | None:
    """Hệ số biến thiên của tổng WBS giữa các lần (--repeat ≥ 2)."""
    if len(values) < 2:
        return None
    mean = statistics.mean(values)
    if mean == 0:
        return None
    return round(statistics.stdev(values) / mean, 3)


def compute_metrics(run: dict[str, Any], expected: dict) -> dict[str, Any]:
    """Tính toàn bộ chỉ số §6.2 cho một lần chạy.

    ``run`` gồm: direction, wbs_total, wbs_by_phase, effort_range,
    traceability {covered,total,covered_codes}, wbs_checks (4 cờ),
    schedule_ok (bool|None), duration_weeks, question_rounds, question_count,
    confidence_level, llm_calls, seconds, wbs_totals_across_repeats.
    """
    expected_range = expected_total_range(expected)
    actual_total = actual_total_for_expected(run.get("wbs_by_phase") or {}, expected)
    trace = run.get("traceability") or {}
    return {
        "direction": run.get("direction"),
        "direction_ok": direction_ok(run.get("direction"), expected.get("acceptable_directions") or []),
        "total_ape": total_ape(actual_total, expected_range),
        "total_in_expected": total_in_expected(actual_total, expected_range),
        "interval_hit": interval_hit(run.get("effort_range"), expected_range),
        "phase_share_error": phase_share_error(run.get("wbs_by_phase") or {}, expected),
        "traceability_pct": traceability_pct(trace.get("covered", 0), trace.get("total", 0)),
        "must_trace_ok": must_trace_ok(trace.get("covered_codes") or set(), expected.get("must_trace") or []),
        "checks_pass": checks_pass(run.get("wbs_checks") or {}, run.get("schedule_ok")),
        "duration_weeks_error": duration_weeks_error(run.get("duration_weeks"), expected),
        "question_rounds": run.get("question_rounds", 0),
        "question_count": run.get("question_count", 0),
        "confidence_level": run.get("confidence_level"),
        "llm_calls": run.get("llm_calls", 0),
        "seconds": round(run.get("seconds", 0.0), 2),
        "stability_cv": stability_cv(run.get("wbs_totals_across_repeats") or []),
    }


def aggregate_metrics(results: list[dict]) -> dict[str, Any]:
    """Tổng hợp §6.3 — MAPE, tỉ lệ total_in_expected, interval_hit, direction_ok,
    trung bình traceability_pct, checks_pass %."""
    n = len(results)
    if n == 0:
        return {}
    ape_values = [r["total_ape"] for r in results if r.get("total_ape") is not None]
    trace_values = [r["traceability_pct"] for r in results if r.get("traceability_pct") is not None]
    return {
        "case_count": n,
        "mape": round(sum(ape_values) / len(ape_values), 1) if ape_values else None,
        "total_in_expected_rate": round(
            sum(1 for r in results if r["total_in_expected"]) / n, 3
        ),
        "interval_hit_rate": round(sum(1 for r in results if r["interval_hit"]) / n, 3),
        "direction_ok_pct": round(
            sum(1 for r in results if r["direction_ok"]) / n * 100, 1
        ),
        "avg_traceability_pct": (
            round(sum(trace_values) / len(trace_values), 1) if trace_values else None
        ),
        "checks_pass_pct": round(
            sum(r["checks_pass"] for r in results) / n * 100, 1
        ),
        "avg_question_rounds": round(
            sum(r["question_rounds"] for r in results) / n, 2
        ),
        "avg_question_count": round(sum(r["question_count"] for r in results) / n, 2),
        "avg_llm_calls": round(sum(r["llm_calls"] for r in results) / n, 1),
        "avg_seconds": round(sum(r["seconds"] for r in results) / n, 2),
    }