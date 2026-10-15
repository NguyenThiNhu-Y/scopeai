"""Test đọc file WBS dự án cũ (thiet_ke_danh_gia.md §3.4).

- 6 file mẫu trong reference/case_studies_wbs/ đọc được, tổng man-day thực tế
  theo giai đoạn khớp actual_man_day của từng case (lệch ≤ 1 → không cảnh báo).
- Điểm nóng: task có thực tế vượt ước lượng > 30%.
- Case thua thầu (không actual_man_day) không bị so sánh.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.services.case_study_service import (
    REFERENCE_WBS_DIR,
    _compare_with_actual,
    parse_wbs_workbook,
)

_CASES_FILE = Path(__file__).resolve().parents[1] / "app" / "reference" / "case_studies.yaml"
CASES = yaml.safe_load(_CASES_FILE.read_text(encoding="utf-8"))
CASES_WITH_WBS = [case for case in CASES if case.get("wbs_file")]


def _parse(case: dict) -> dict:
    path = REFERENCE_WBS_DIR / case["wbs_file"]
    assert path.is_file(), f"Thiếu file WBS mẫu: {path}"
    return parse_wbs_workbook(path.read_bytes())


def test_all_six_sample_wbs_files_exist():
    assert len(CASES_WITH_WBS) == 6
    for case in CASES_WITH_WBS:
        assert (REFERENCE_WBS_DIR / case["wbs_file"]).is_file()


@pytest.mark.parametrize("case", CASES_WITH_WBS, ids=lambda case: case["id"])
def test_wbs_totals_match_actual_man_day(case):
    parse = _parse(case)
    expected = case.get("actual_man_day")
    if expected is None:
        # Case thua thầu: WBS chỉ có ước lượng → tổng thực tế 0, không cảnh báo.
        assert parse["total_actual"] == 0
        assert _compare_with_actual(parse, case) == []
        return
    for phase in ("poc", "mvp", "production"):
        assert abs(parse["by_phase"][phase]["actual"] - expected[phase]) <= 1, (
            f"{case['id']} {phase}: {parse['by_phase'][phase]['actual']} vs {expected[phase]}"
        )
    assert _compare_with_actual(parse, case) == []


def test_hotspots_detected_for_known_case():
    case = next(c for c in CASES_WITH_WBS if c["id"] == "cs_rag_mc_manual_aichi")
    parse = _parse(case)
    assert len(parse["hotspots"]) == 7
    for hotspot in parse["hotspots"]:
        assert hotspot["actual_man_day"] > hotspot["estimated_man_day"] * 1.3
        assert hotspot["task_code"]
        assert hotspot["name_vi"]
        assert hotspot["phase"] in ("poc", "mvp", "production")


def test_requirement_codes_extracted_from_wbs_sheet():
    case = next(c for c in CASES_WITH_WBS if c["id"] == "cs_rag_mc_manual_aichi")
    parse = _parse(case)
    assert "R-DOC-02" in parse["requirement_codes"]
    assert "R-HIS-01" in parse["requirement_codes"]


def test_compare_warns_when_totals_mismatch():
    case = next(c for c in CASES_WITH_WBS if c["id"] == "cs_rag_mc_manual_aichi")
    parse = _parse(case)
    shifted = dict(case)
    shifted["actual_man_day"] = {"poc": 1, "mvp": 1, "production": 1}
    warnings = _compare_with_actual(parse, shifted)
    assert len(warnings) == 3
    assert any("poc" in warning for warning in warnings)


def test_parse_rejects_missing_wbs_sheet():
    from io import BytesIO

    from openpyxl import Workbook

    from app.api.errors import ApiError

    wb = Workbook()
    wb.active.title = "Khác"
    output = BytesIO()
    wb.save(output)
    with pytest.raises(ApiError) as exc_info:
        parse_wbs_workbook(output.getvalue())
    assert "WBS" in str(exc_info.value.message)


def test_download_wbs_endpoint_serves_reference_file(client):
    """GET /api/settings/case_studies/{id}/wbs trả file mặc định trong reference."""
    resp = client.get("/api/settings/case_studies/cs_rag_mc_manual_aichi/wbs")
    assert resp.status_code == 200
    assert "spreadsheetml" in resp.headers["content-type"]
    assert "attachment" in resp.headers["content-disposition"]
    assert resp.content[:2] == b"PK"  # magic ZIP của xlsx


def test_download_wbs_404_for_case_without_file(client):
    resp = client.get("/api/settings/case_studies/cs_none_crm_jp/wbs")
    assert resp.status_code == 404


def test_upload_wbs_endpoint_parses_and_updates_case(client):
    """POST /api/settings/case_studies/{id}/wbs parse + cập nhật wbs_file."""
    case = next(c for c in CASES_WITH_WBS if c["id"] == "cs_rag_mc_manual_aichi")
    data = (REFERENCE_WBS_DIR / case["wbs_file"]).read_bytes()
    resp = client.post(
        "/api/settings/case_studies/cs_none_crm_jp/wbs",
        files={"file": ("uploaded_wbs.xlsx", data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers={"X-Actor": "tester"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["case_id"] == "cs_none_crm_jp"
    assert body["wbs_file"] == "uploaded_wbs.xlsx"
    assert body["total_actual"] == 573.0
    assert len(body["hotspots"]) == 7
    # wbs_file của case đã được cập nhật trong settings (phiên bản mới).
    assert body["version"] >= 2
    # Tải về file vừa upload.
    resp = client.get("/api/settings/case_studies/cs_none_crm_jp/wbs")
    assert resp.status_code == 200
    assert resp.content == data