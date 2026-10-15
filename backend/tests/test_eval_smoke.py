"""Smoke test eval harness — thiet_ke_danh_gia.md §6.

Chạy 1 golden case với mock, assert báo cáo (md + json) được sinh ra đúng cấu
trúc. KHÔNG gọi LLM thật (BR-03) — conftest ép LLM_PROVIDER=mock.
"""

from __future__ import annotations

import json
from pathlib import Path

from eval.report import write_report
from eval.run_eval import run_eval


def test_eval_smoke_runs_one_case_and_writes_report(tmp_path):
    report = run_eval(case_ids=["gc_crm_ja"], repeat=1)
    paths = write_report(report, reports_dir=tmp_path)

    assert report["provider"] == "mock"
    assert report["model"] == "mock"
    assert report["case_ids"] == ["gc_crm_ja"]
    assert report["repeat"] == 1
    assert "gc_crm_ja" in report["per_case"]
    assert report["summary"]["case_count"] == 1

    # Báo cáo md + json được ghi vào thư mục chỉ định.
    files = sorted(tmp_path.glob("eval_*_mock.*"))
    assert len(files) == 2
    md_files = [f for f in files if f.suffix == ".md"]
    json_files = [f for f in files if f.suffix == ".json"]
    assert len(md_files) == 1 and len(json_files) == 1

    md = md_files[0].read_text(encoding="utf-8")
    assert "Mock chỉ kiểm tra harness, không đo chất lượng AI" in md
    assert "gc_crm_ja" in md
    assert "MAPE" in md

    data = json.loads(json_files[0].read_text(encoding="utf-8"))
    assert data["provider"] == "mock"
    metrics = data["per_case"]["gc_crm_ja"][0]
    for key in (
        "direction_ok",
        "total_ape",
        "total_in_expected",
        "interval_hit",
        "phase_share_error",
        "traceability_pct",
        "must_trace_ok",
        "checks_pass",
        "duration_weeks_error",
        "question_rounds",
        "question_count",
        "confidence_level",
        "llm_calls",
        "seconds",
    ):
        assert key in metrics


def test_eval_smoke_metrics_are_measured(tmp_path):
    """Với mock, các chỉ số phải có giá trị thực (không phải None)."""
    report = run_eval(case_ids=["gc_crm_ja"], repeat=1)
    metrics = report["per_case"]["gc_crm_ja"][0]
    assert metrics["direction_ok"] in (True, False)
    assert metrics["total_ape"] is not None
    assert metrics["interval_hit"] in (True, False)
    assert metrics["llm_calls"] > 0  # pipeline đã gọi mock LLM
    assert metrics["seconds"] >= 0
    assert metrics["confidence_level"] in ("high", "medium", "low")