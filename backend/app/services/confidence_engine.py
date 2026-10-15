"""Độ tin cậy từng hồ sơ — thiet_ke_danh_gia.md §5.

Hàm THUẦN: đầu vào là dict dữ liệu hồ sơ đã có (intake, questions, evaluations,
WBS check, schedule, effort, case studies), đầu ra là dict khớp ``ConfidenceOut``
§5.1. KHÔNG gọi LLM, KHÔNG import gateway, KHÔNG đọc DB — service tầng trên
(confidence_service) lo việc gom dữ liệu.

Nguyên tắc (thiet_ke_danh_gia.md §2): độ tin cậy do CODE tính; LLM không sinh
điểm/phần trăm; mức Cao/Trung bình/Thấp kèm danh sách lý do kiểm chứng được;
dưới 2 case tương tự → trạng thái "Chưa đủ dữ liệu tham chiếu" (na), không kết luận.
"""

from __future__ import annotations

import re
import statistics
from typing import Any

SIGNAL_LABELS: dict[str, str] = {
    "input_completeness": "Đầu vào",
    "wbs_checks": "Kiểm tra WBS",
    "schedule_checks": "Kiểm tra lịch",
    "traceability": "Truy vết requirement",
    "coverage_uncertainty": "Độ chắc của đánh giá đáp ứng",
    "analog": "So với dự án tương tự",
    "history_bias": "Sai lệch lịch sử",
}

STATUS_LABELS: dict[str, str] = {
    "pass": "Đạt",
    "warn": "Cảnh báo",
    "fail": "Lỗi",
    "na": "Chưa đủ dữ liệu",
}

LEVEL_LABELS: dict[str, str] = {
    "high": "Cao",
    "medium": "Trung bình",
    "low": "Thấp",
}


def _rules(thresholds: dict[str, Any]) -> dict[str, Any]:
    """Chấp nhận cả payload đầy đủ ({version, thresholds}) lẫn rules trực tiếp."""
    return thresholds.get("thresholds", thresholds)


def _signal(key: str, status: str, detail_vi: str, data: dict[str, Any]) -> dict:
    return {
        "key": key,
        "label_vi": SIGNAL_LABELS[key],
        "status": status,
        "detail_vi": detail_vi,
        "data": data,
    }


# ---------------------------------------------------------------- tìm case tương tự (§5.4)

def _keyword_tokens(text: str | None) -> set[str]:
    """Token từ khóa (chữ ≥ 3 ký tự, lower) — dùng so khớp ngành/tiêu đề."""
    if not text:
        return set()
    return {token for token in re.findall(r"\w+", text.lower()) if len(token) >= 3}


def keyword_overlap(case: dict, summary_keywords: set[str]) -> float:
    """Tỉ lệ từ khóa ngành/tiêu đề của case xuất hiện trong tóm tắt intake (0–1)."""
    case_keywords = _keyword_tokens(case.get("title")) | _keyword_tokens(
        case.get("industry")
    )
    if not case_keywords:
        return 0.0
    return len(case_keywords & summary_keywords) / len(case_keywords)


def similarity_score(
    case: dict,
    *,
    market: str | None,
    customer_language: str | None,
    requirement_count: int | None,
    summary_keywords: set[str],
    weights: dict[str, float],
) -> float:
    """Điểm tương đồng 0–1 (thiet_ke_danh_gia.md §5.4, công thức cố định).

    0,4 × cùng market + 0,3 × (1 − min(|req_a−req_b|/max(req_a,req_b), 1))
    + 0,2 × cùng ngôn ngữ khách + 0,1 × trùng từ khóa ngành/tiêu đề.
    """
    market_score = 1.0 if case.get("market") == market else 0.0

    req_a = case.get("requirement_count") or 0
    req_b = requirement_count or 0
    if req_a == 0 and req_b == 0:
        req_score = 1.0
    else:
        req_score = 1 - min(abs(req_a - req_b) / max(req_a, req_b, 1), 1)

    lang_score = 1.0 if case.get("customer_language") == customer_language else 0.0
    kw_score = keyword_overlap(case, summary_keywords)

    return (
        weights.get("market", 0.4) * market_score
        + weights.get("requirement_count", 0.3) * req_score
        + weights.get("language", 0.2) * lang_score
        + weights.get("keyword", 0.1) * kw_score
    )


def _actual_total(case: dict) -> float:
    return round(sum(float(v) for v in (case.get("actual_man_day") or {}).values()), 1)


def find_similar_cases(
    case_studies: list[dict],
    *,
    direction: str | None,
    market: str | None,
    customer_language: str | None,
    requirement_count: int | None,
    summary_keywords: set[str],
    thresholds: dict[str, Any],
) -> list[dict]:
    """Lọc cùng hướng + có actual_man_day; lấy ≤ 3 case điểm ≥ 0,5 giảm dần."""
    thresholds = _rules(thresholds)
    weights = thresholds["similarity"]["weights"]
    min_score = thresholds["similarity"]["min_score"]
    max_cases = thresholds["similarity"]["max_cases"]

    scored: list[dict] = []
    for case in case_studies:
        if case.get("direction") != direction or not case.get("actual_man_day"):
            continue
        score = similarity_score(
            case,
            market=market,
            customer_language=customer_language,
            requirement_count=requirement_count,
            summary_keywords=summary_keywords,
            weights=weights,
        )
        if score < min_score:
            continue
        scored.append(
            {
                "id": case["id"],
                "title": case.get("title", ""),
                "similarity": round(score, 2),
                "direction": case.get("direction"),
                "market": case.get("market"),
                "requirement_count": case.get("requirement_count"),
                "actual_man_day": case.get("actual_man_day"),
                "actual_total": _actual_total(case),
                "actual_duration_weeks": case.get("actual_duration_weeks"),
            }
        )
    scored.sort(key=lambda item: (-item["similarity"], item["id"]))
    return scored[:max_cases]


def history_bias(
    case_studies: list[dict], direction: str | None, thresholds: dict[str, Any]
) -> dict | None:
    """Trung vị (thực tế ÷ ước lượng) của case cùng hướng — cần ≥ 2 case.

    Trả None khi chưa đủ dữ liệu (tín hiệu sẽ là na).
    """
    thresholds = _rules(thresholds)
    ratios: list[float] = []
    for case in case_studies:
        if case.get("direction") != direction:
            continue
        estimated = case.get("estimated_man_day")
        actual = case.get("actual_man_day")
        if not estimated or not actual:
            continue
        est_total = sum(float(v) for v in estimated.values())
        if est_total <= 0:
            continue
        ratios.append(sum(float(v) for v in actual.values()) / est_total)
    if len(ratios) < 2:
        return None
    median = statistics.median(ratios)
    pass_min = thresholds["history_bias"]["pass_min"]
    pass_max = thresholds["history_bias"]["pass_max"]
    if pass_min <= median <= pass_max:
        label = "none"
    elif median > pass_max:
        label = "above"
    else:
        label = "below"
    return {
        "direction": label,
        "median_actual_over_estimate": round(median, 2),
        "case_count": len(ratios),
    }


# ---------------------------------------------------------------- 7 tín hiệu (§5.2)

def signal_input_completeness(data: dict, thresholds: dict[str, Any]) -> dict:
    bid = data.get("bid") or {}
    has_budget = bid.get("budget_amount") is not None
    has_start = bool(bid.get("customer_schedule_start"))
    has_milestone = bool(bid.get("customer_mvp_start") or bid.get("customer_production_start"))
    # "Có file requirement" do service xác định từ attachment thật (ground truth).
    has_req_file = bool(bid.get("has_requirement_file", not bid.get("no_requirement_file")))
    present = [has_budget, has_start, has_milestone, has_req_file]
    missing = 4 - sum(bool(item) for item in present)
    blocking = int((data.get("questions") or {}).get("blocking_unanswered") or 0)

    warn_max = thresholds["input_completeness"]["warn_missing_max"]
    detail_items: list[str] = []
    if not has_budget:
        detail_items.append("thiếu ngân sách")
    if not has_start:
        detail_items.append("thiếu mốc bắt đầu khách")
    if not has_milestone:
        detail_items.append("thiếu mốc MVP/Production khách")
    if not has_req_file:
        detail_items.append("thiếu file requirement")
    if blocking:
        detail_items.append(f"{blocking} câu hỏi chặn chưa trả lời")

    if blocking > 0:
        status = "fail"
    elif missing > warn_max:
        status = "fail"
    elif missing >= 1:
        status = "warn"
    else:
        status = "pass"

    detail_vi = (
        "Đủ 4 mục đầu vào, không còn câu hỏi chặn"
        if status == "pass"
        else "Thiếu: " + ", ".join(detail_items)
    )
    return _signal(
        "input_completeness",
        status,
        detail_vi,
        {
            "has_budget": has_budget,
            "has_start": has_start,
            "has_milestone": has_milestone,
            "has_requirement_file": has_req_file,
            "blocking_unanswered": blocking,
            "missing_count": missing,
        },
    )


# Tên cờ WBS → lý do tiếng Việt (Đợt 14 D2 — không hiện mã thô).
_WBS_FLAG_REASONS: dict[str, str] = {
    "pm_qa_ok": "thiếu PM/QA ở một giai đoạn",
    "within_20pct": "lệch ngoài ±20% so với midpoint",
    "cycle_free": "có vòng phụ thuộc",
    "leaf_within_limit": "có task lá vượt 10 man-day",
}


def signal_wbs_checks(data: dict, thresholds: dict[str, Any]) -> dict:
    check = data.get("wbs_check")
    if not check:
        return _signal(
            "wbs_checks", "na", "Chưa có WBS để kiểm tra", {"passed": 0, "total": 4, "flags": {}}
        )
    flags = thresholds["wbs_checks"]["required_flags"]
    values = {flag: bool(check.get(flag)) for flag in flags}
    passed = sum(values.values())
    status = "pass" if passed == len(flags) else "fail"
    failed_names = [flag for flag, ok in values.items() if not ok]
    if status == "pass":
        detail_vi = "4/4 kiểm tra WBS đạt"
    else:
        reasons = [
            _WBS_FLAG_REASONS[flag] if flag in _WBS_FLAG_REASONS else flag
            for flag in failed_names
        ]
        detail_vi = f"Thiếu {len(failed_names)} kiểm tra WBS: " + ", ".join(reasons)
    return _signal(
        "wbs_checks", status, detail_vi, {"passed": passed, "total": len(flags), "flags": values}
    )


def _late_days(end_date: str | None, customer_end: str | None) -> int | None:
    if not end_date or not customer_end:
        return None
    from datetime import date

    return (date.fromisoformat(end_date) - date.fromisoformat(customer_end)).days


def signal_schedule_checks(data: dict, thresholds: dict[str, Any]) -> dict:
    schedule = data.get("schedule")
    if not schedule:
        return _signal(
            "schedule_checks", "na", "Chưa có lịch để kiểm tra", {"checks": {}, "late_days": None}
        )
    bid = data.get("bid") or {}

    mvp_start = schedule.get("earliest_mvp_start")
    go_no_go_end = schedule.get("go_no_go_end")
    production_start = schedule.get("earliest_production_start")
    end_date = schedule.get("end_date")
    customer_end = bid.get("customer_schedule_end")

    mvp_ok = True
    if mvp_start and go_no_go_end:
        mvp_ok = mvp_start >= go_no_go_end
    prod_ok = True
    if production_start and mvp_start:
        prod_ok = production_start > mvp_start
    late = _late_days(end_date, customer_end)
    end_ok = late is None or late <= 0
    no_warning = not bool(schedule.get("warning"))

    warn_late_days = thresholds["schedule"]["warn_late_days"]
    checks = {"mvp_after_go_no_go": mvp_ok, "production_after_mvp": prod_ok, "end_within_customer": end_ok}

    if not mvp_ok or not prod_ok:
        status = "fail"
        detail_vi = "Sai thứ tự giai đoạn: MVP trước go/no-go hoặc Production trước MVP"
    elif late is not None and late > warn_late_days:
        status = "fail"
        detail_vi = f"Lịch kết thúc trễ hơn mốc khách {late} ngày (> {warn_late_days} ngày)"
    elif late is not None and late > 0:
        status = "warn"
        detail_vi = f"Lịch kết thúc trễ hơn mốc khách {late} ngày (≤ {warn_late_days} ngày)"
    elif not no_warning:
        status = "warn"
        detail_vi = schedule["warning"]
    else:
        status = "pass"
        detail_vi = "Lịch đạt: đúng thứ tự giai đoạn, kết thúc trong mốc khách, không cảnh báo"

    return _signal(
        "schedule_checks",
        status,
        detail_vi,
        {"checks": checks, "late_days": late, "warning": schedule.get("warning")},
    )


def signal_traceability(data: dict, thresholds: dict[str, Any]) -> dict:
    requirements = data.get("requirements") or {}
    total = int(requirements.get("total") or 0)
    covered = int(requirements.get("covered") or 0)
    if total <= 0:
        return _signal(
            "traceability", "na", "Chưa có requirement để truy vết",
            {"covered": 0, "total": 0, "ratio": None, "uncovered": []},
        )
    ratio = covered / total
    pass_min = thresholds["traceability"]["pass_min"]
    warn_min = thresholds["traceability"]["warn_min"]
    if ratio >= pass_min:
        status = "pass"
    elif ratio >= warn_min:
        status = "warn"
    else:
        status = "fail"
    detail_vi = f"{covered}/{total} requirement có task"
    return _signal(
        "traceability",
        status,
        detail_vi,
        {
            "covered": covered,
            "total": total,
            "ratio": round(ratio, 3),
            "uncovered": requirements.get("uncovered") or [],
        },
    )


def signal_coverage_uncertainty(data: dict, thresholds: dict[str, Any]) -> dict:
    evaluations = data.get("evaluations") or {}
    total = int(evaluations.get("total") or 0)
    uncertain = int(evaluations.get("uncertain") or 0)
    if total <= 0:
        return _signal(
            "coverage_uncertainty", "na", "Chưa có đánh giá đáp ứng",
            {"uncertain": 0, "total": 0, "ratio": None},
        )
    ratio = uncertain / total
    pass_max = thresholds["coverage_uncertainty"]["pass_max"]
    warn_max = thresholds["coverage_uncertainty"]["warn_max"]
    if ratio <= pass_max:
        status = "pass"
    elif ratio <= warn_max:
        status = "warn"
    else:
        status = "fail"
    detail_vi = f"{uncertain}/{total} đánh giá chưa chắc chắn (△/×/cần làm rõ)"
    return _signal(
        "coverage_uncertainty",
        status,
        detail_vi,
        {"uncertain": uncertain, "total": total, "ratio": round(ratio, 3)},
    )


def signal_analog(
    data: dict, similar_cases: list[dict], thresholds: dict[str, Any]
) -> dict:
    estimate_total = data.get("wbs_total")
    effort_midpoint = (data.get("effort") or {}).get("midpoint_total")
    if len(similar_cases) < 2:
        return _signal(
            "analog",
            "na",
            f"Chưa đủ dữ liệu tham chiếu: {len(similar_cases)} case tương tự",
            {
                "cases": similar_cases,
                "actual_total_range": [],
                "estimate_total": estimate_total,
                "effort_midpoint": effort_midpoint,
                "position": "insufficient",
            },
        )
    totals = [case["actual_total"] for case in similar_cases]
    extend = thresholds["analog"]["range_extend_pct"] / 100.0
    warn_outside = thresholds["analog"]["warn_outside_pct"] / 100.0
    range_low = min(totals) * (1 - extend)
    range_high = max(totals) * (1 + extend)
    actual_range = [round(min(totals), 1), round(max(totals), 1)]

    # Nhãn vị trí tiếng Việt — không hiện mã thô below/above/inside (Đợt 14 D2).
    position_label = {"below": "thấp hơn", "above": "cao hơn", "inside": "nằm trong"}

    if estimate_total is None:
        position = "insufficient"
        deviation = 0.0
        status = "na"
        detail_vi = "Chưa có tổng WBS để so sánh"
    elif estimate_total < range_low:
        position = "below"
        # % lệch tính so với KHOẢNG THỰC TẾ GỐC (min thật), không phải khoảng
        # đã nới ±10% — Đợt 14 D2.
        deviation = (min(totals) - estimate_total) / min(totals)
        if deviation <= warn_outside:
            status = "warn"
            detail_vi = f"Tổng WBS {estimate_total} {position_label[position]} khoảng thực tế {actual_range} (lệch {round(deviation * 100, 1)}%)"
        else:
            status = "fail"
            detail_vi = f"Tổng WBS {estimate_total} {position_label[position]} khoảng thực tế {actual_range} quá {round(warn_outside * 100, 1)}%"
    elif estimate_total > range_high:
        position = "above"
        deviation = (estimate_total - max(totals)) / max(totals)
        if deviation <= warn_outside:
            status = "warn"
            detail_vi = f"Tổng WBS {estimate_total} {position_label[position]} khoảng thực tế {actual_range} (lệch {round(deviation * 100, 1)}%)"
        else:
            status = "fail"
            detail_vi = f"Tổng WBS {estimate_total} {position_label[position]} khoảng thực tế {actual_range} quá {round(warn_outside * 100, 1)}%"
    else:
        position = "inside"
        deviation = 0.0
        status = "pass"
        detail_vi = f"Tổng WBS {estimate_total} {position_label[position]} khoảng thực tế {actual_range} (±{thresholds['analog']['range_extend_pct']}%)"

    return _signal(
        "analog",
        status,
        detail_vi,
        {
            "cases": similar_cases,
            "actual_total_range": actual_range,
            "estimate_total": estimate_total,
            "effort_midpoint": effort_midpoint,
            "position": position,
        },
    )


def signal_history_bias(
    data: dict, bias: dict | None, thresholds: dict[str, Any]
) -> dict:
    if bias is None:
        return _signal(
            "history_bias",
            "na",
            "Chưa đủ dữ liệu tham chiếu: dưới 2 case cùng hướng có effort thực tế",
            {"direction": None, "median_actual_over_estimate": None, "case_count": 0},
        )
    pass_min = thresholds["history_bias"]["pass_min"]
    pass_max = thresholds["history_bias"]["pass_max"]
    median = bias["median_actual_over_estimate"]
    if pass_min <= median <= pass_max:
        status = "pass"
    else:
        status = "warn"
    trend = "cao hơn" if bias["direction"] == "above" else ("thấp hơn" if bias["direction"] == "below" else "tương đương")
    detail_vi = (
        f"Trung vị thực tế/ước lượng {median} ({trend} ước lượng, {bias['case_count']} case cùng hướng)"
    )
    return _signal(
        "history_bias",
        status,
        detail_vi,
        {
            "direction": bias["direction"],
            "median_actual_over_estimate": median,
            "case_count": bias["case_count"],
        },
    )


# ---------------------------------------------------------------- ra mức (§5.3)

def decide_level(signals: list[dict], thresholds: dict[str, Any]) -> dict:
    """Quy tắc cố định §5.3 — Thấp/Trung bình/Cao + summary_vi (tối đa 3 lý do)."""
    thresholds = _rules(thresholds)
    important = set(thresholds["level_rules"]["important_signals"])
    fails = [s for s in signals if s["status"] == "fail"]
    warns = [s for s in signals if s["status"] == "warn"]
    important_fail = any(s["key"] in important for s in fails)

    if important_fail or len(fails) >= thresholds["level_rules"]["min_fail_for_low"]:
        level = "low"
    elif len(fails) >= 1 or len(warns) >= thresholds["level_rules"]["min_warn_for_medium"]:
        level = "medium"
    else:
        level = "high"

    reasons = [f"{s['label_vi']}: {s['detail_vi']}" for s in fails + warns]
    max_reasons = thresholds["level_rules"]["max_summary_reasons"]
    if reasons:
        summary_vi = "Cảnh báo: " + "; ".join(reasons[:max_reasons])
    else:
        summary_vi = "Hồ sơ đạt các kiểm tra độ tin cậy chính."

    return {
        "level": level,
        "level_label_vi": LEVEL_LABELS[level],
        "summary_vi": summary_vi,
    }


# ---------------------------------------------------------------- tổng hợp

def compute_confidence(
    data: dict[str, Any], thresholds: dict[str, Any]
) -> dict[str, Any]:
    """Tính toàn bộ kết quả độ tin cậy từ dữ liệu hồ sơ (hàm thuần).

    ``data`` gồm: bid, direction, questions, requirements, evaluations,
    wbs_check, wbs_total, effort, schedule, case_studies.
    """
    thresholds = _rules(thresholds)
    bid = data.get("bid") or {}
    direction = data.get("direction")
    similar = find_similar_cases(
        data.get("case_studies") or [],
        direction=direction,
        market=bid.get("market"),
        customer_language=bid.get("customer_language"),
        requirement_count=(data.get("requirements") or {}).get("total"),
        summary_keywords=_keyword_tokens(bid.get("request_content")),
        thresholds=thresholds,
    )
    bias = history_bias(data.get("case_studies") or [], direction, thresholds)

    signals = [
        signal_input_completeness(data, thresholds),
        signal_wbs_checks(data, thresholds),
        signal_schedule_checks(data, thresholds),
        signal_traceability(data, thresholds),
        signal_coverage_uncertainty(data, thresholds),
        signal_analog(data, similar, thresholds),
        signal_history_bias(data, bias, thresholds),
    ]

    level = decide_level(signals, thresholds)

    analog_signal = next(s for s in signals if s["key"] == "analog")
    history_signal = next(s for s in signals if s["key"] == "history_bias")
    return {
        **level,
        "signals": signals,
        "analog": {
            **analog_signal["data"],
            "history_bias": history_signal["data"],
        },
    }