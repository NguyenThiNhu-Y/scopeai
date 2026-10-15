"""Ghi báo cáo eval — thiet_ke_danh_gia.md §6.3.

Đầu ra: ``docs/eval/reports/eval_<YYYYMMDD_HHMM>_<provider>.md`` và ``.json``.
Báo cáo ghi rõ provider và model; với mock ghi chú "Mock chỉ kiểm tra harness,
không đo chất lượng AI".
"""

from __future__ import annotations

import json
import time
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parents[2] / "docs" / "eval" / "reports"

_STATUS_VI = {
    "pass": "Đạt",
    "warn": "Cảnh báo",
    "fail": "Lỗi",
    "na": "Chưa đủ dữ liệu",
}

_LEVEL_VI = {"high": "Cao", "medium": "Trung bình", "low": "Thấp"}


def _metric_line(label: str, value, suffix: str = "") -> str:
    if value is None:
        return f"| {label} | — |"
    return f"| {label} | {value}{suffix} |"


def _case_rows(case_id: str, results: list[dict]) -> str:
    rows = []
    for index, result in enumerate(results, start=1):
        label = case_id if len(results) == 1 else f"{case_id} (lần {index})"
        confidence = result.get("confidence_level")
        rows.append(
            f"| {label} | {result.get('direction') or '—'} | "
            f"{result['direction_ok']} | {result.get('total_ape')}% | "
            f"{result['total_in_expected']} | {result['interval_hit']} | "
            f"{result.get('phase_share_error')} | {result.get('traceability_pct')}% | "
            f"{result['must_trace_ok']} | {result['checks_pass']} | "
            f"{result.get('duration_weeks_error')} | "
            f"{_LEVEL_VI.get(confidence, confidence) if confidence else '—'} | "
            f"{result['question_rounds']} | {result['question_count']} | "
            f"{result['llm_calls']} | {result['seconds']} | "
            f"{result.get('stability_cv') if result.get('stability_cv') is not None else '—'} |"
        )
    return "\n".join(rows)


def render_markdown(report: dict) -> str:
    summary = report.get("summary") or {}
    mock_note = (
        "\n> **Mock chỉ kiểm tra harness, không đo chất lượng AI.**\n"
        if report.get("provider") == "mock"
        else ""
    )
    lines = [
        "# Báo cáo đánh giá hệ thống (eval)",
        "",
        f"- **Provider:** {report['provider']}",
        f"- **Model:** {report['model']}",
        f"- **Thời gian chạy:** {report.get('started_at')}",
        f"- **Số lần chạy mỗi case:** {report.get('repeat')}",
        f"- **Case:** {', '.join(report.get('case_ids') or [])}",
        "",
        mock_note,
        "## Tổng hợp",
        "",
        "| Chỉ số | Giá trị |",
        "|---|---|",
    ]
    lines.append(_metric_line("MAPE (trung bình total_ape)", summary.get("mape"), "%"))
    lines.append(_metric_line("Tỉ lệ total_in_expected", summary.get("total_in_expected_rate")))
    lines.append(_metric_line("Tỉ lệ interval_hit", summary.get("interval_hit_rate")))
    lines.append(_metric_line("Direction đúng (%)", summary.get("direction_ok_pct")))
    lines.append(_metric_line("Trung bình traceability_pct", summary.get("avg_traceability_pct"), "%"))
    lines.append(_metric_line("Checks pass (%)", summary.get("checks_pass_pct")))
    lines.append(_metric_line("Trung bình vòng hỏi", summary.get("avg_question_rounds")))
    lines.append(_metric_line("Trung bình số câu hỏi", summary.get("avg_question_count")))
    lines.append(_metric_line("Trung bình số lần gọi LLM", summary.get("avg_llm_calls")))
    lines.append(_metric_line("Trung bình thời gian (giây)", summary.get("avg_seconds")))
    lines.extend([
        "",
        "## Từng case",
        "",
        "| Case | Hướng | Direction đúng | APE | Trong khoảng | Interval hit | "
        "Sai lệch tỉ trọng | Truy vết % | Must-trace | Checks pass | "
        "Sai lệch tuần | Độ tin cậy | Vòng hỏi | Số câu hỏi | Gọi LLM | Giây | Stability CV |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ])
    for case_id, results in (report.get("per_case") or {}).items():
        lines.append(_case_rows(case_id, results))
    lines.extend(["", f"*Tổng thời gian chạy: {report.get('seconds')} giây.*"])
    return "\n".join(lines)


def write_report(report: dict, reports_dir: Path | None = None) -> dict[str, Path]:
    """Ghi báo cáo md + json; trả đường dẫn. Idempotent theo timestamp."""
    target = reports_dir or REPORTS_DIR
    target.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M")
    base = target / f"eval_{stamp}_{report['provider']}"
    md_path = base.with_suffix(".md")
    json_path = base.with_suffix(".json")

    md_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return {"md": md_path, "json": json_path}