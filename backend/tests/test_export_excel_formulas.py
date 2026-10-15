from io import BytesIO
from types import SimpleNamespace

import openpyxl

from app.exporters.estimate_xlsx import render_estimate


def _item(code, name, phase="poc", parent=None, role=None, man_day=None):
    return SimpleNamespace(task_code=code, name_vi=name, phase=phase, parent_code=parent, role=role, man_day=man_day, requirement_codes=["REQ-001"] if role else None)


def _data(approved=False):
    return {
        "project_name": "Dự án giả lập",
        "customer_name": "Khách hàng giả lập",
        "customer_language": "ja",
        "currency": "JPY",
        "export_date": "2026-10-15",
        "quotation": "[Presales điền]" if not approved else "1,000,000 JPY",
        "approved": approved,
        "total": 1000000 if approved else None,
        "quotation_detail": {
            "contract_model": "fixed_price", "tax_mode": "tax_excluded",
            "by_role": {"backend": {"man_day": 2.0, "rate": 400000, "amount": 800000}},
            "overhead": {"pm": 100000, "brse": 0}, "contingency_amount": 50000, "operating_cost": 0,
            "grand_total": 1000000, "by_phase": {"poc": 1000000}, "phase_man_days": {"poc": 2.0},
        } if approved else {"contract_model": "fixed_price", "tax_mode": "tax_excluded", "by_role": {"backend": {"man_day": 2.0}}, "phase_man_days": {"poc": 2.0}},
        "wbs": [_item("1", "Thiết kế"), _item("1.1", "Thiết kế giả lập", parent="1", role="backend", man_day=2)],
        "schedule": {
            "start_date": "2026-11-02", "end_date": "2026-11-20",
            "tasks": [{"task_code": "1.1", "phase": "poc", "role": "backend", "man_day": 2, "start_date": "2026-11-02", "end_date": "2026-11-13"}],
            "payment_milestones": [{"name": "Kickoff", "percent": 30, "due_date": "2026-11-02"}, {"name": "Nghiệm thu", "percent": 70, "due_date": "2026-11-20"}],
        },
        "customer_deadline": "2026-11-27",
        "questions": [SimpleNamespace(id=1, round_no=1, question="Câu hỏi giả lập", reason_vi="Lý do", impact="solution", answer=None, is_assumption=False, status="awaiting_answer")],
    }


def _load(data):
    return openpyxl.load_workbook(BytesIO(render_estimate(data)), data_only=False)


def test_excel_has_required_sheets_and_wbs_formulas():
    workbook = _load(_data())
    assert workbook.sheetnames == ["Tóm tắt", "WBS", "Báo giá", "Lịch Gantt", "Q&A"]
    wbs = workbook["WBS"]
    assert [wbs.cell(1, c).value for c in range(1, 8)] == ["Mã", "Công việc", "Giai đoạn", "Cấp", "Vai trò", "Man-day", "Requirement"]
    assert wbs["F2"].value is None and wbs["D2"].value == 1
    assert wbs["F3"].value == 2 and wbs["D3"].value == 2 and wbs["E3"].value == "Backend"
    assert wbs["F4"].value == "=SUM(F2:F3)"
    assert wbs["F5"].value == '=SUMIF(C2:C3,"PoC",F2:F3)'
    assert workbook["Tóm tắt"]["B9"].value == "=WBS!F4"


def test_approved_quotation_lines_sum_to_grand_total_with_formula():
    workbook = _load(_data(approved=True))
    sheet = workbook["Báo giá"]
    rows = {sheet.cell(r, 1).value: r for r in range(1, sheet.max_row + 1)}
    total_row = rows["Tổng (chưa thuế)"]
    first = rows["Backend"]
    assert sheet.cell(total_row, 4).value == f"=SUM(D{first}:D{total_row - 1})"
    amounts = [sheet.cell(r, 4).value for r in range(first, total_row)]
    assert sum(amounts) == 1000000
    assert workbook["Tóm tắt"]["B10"].value == f"='Báo giá'!D{total_row}"
    kickoff = rows["Kickoff"]
    assert sheet.cell(kickoff, 4).value == f"=ROUND($D${total_row}*B{kickoff}/100,0)"


def test_gantt_has_week_columns_bars_and_milestones():
    sheet = _load(_data())["Lịch Gantt"]
    headers = [sheet.cell(1, c).value for c in range(1, sheet.max_column + 1)]
    assert headers[:6] == ["Mã", "Công việc", "Giai đoạn", "Vai trò", "Bắt đầu", "Kết thúc"]
    week_headers = headers[6:]
    assert len(week_headers) >= 4 and week_headers[0].startswith("W01")
    assert sheet.cell(2, 1).value == "1.1" and sheet.cell(2, 2).value == "Thiết kế giả lập"
    assert sheet.cell(2, 7).fill.fgColor.rgb.endswith("8FAADC")
    assert sheet.cell(2, 8).fill.fgColor.rgb.endswith("8FAADC")
    assert sheet.cell(2, 9).fill.fill_type is None
    labels = [sheet.cell(r, 2).value for r in range(3, sheet.max_row + 1)]
    assert "◆ Kickoff (30%)" in labels and "▲ Hạn khách yêu cầu" in labels


def test_qna_sheet_uses_readable_labels_and_yellow_answer():
    sheet = _load(_data())["Q&A"]
    assert sheet["C2"].value == "Câu hỏi giả lập"
    assert sheet["E2"].value == "Giải pháp"
    assert sheet["G2"].value == "Không"
    assert sheet["H2"].value == "Chờ trả lời"
    assert sheet["F2"].fill.fgColor.rgb.endswith("FFFF00")


def test_empty_wbs_still_has_valid_sum_range():
    data = _data()
    data["wbs"] = []
    data["schedule"] = None
    workbook = _load(data)
    assert workbook["WBS"]["F3"].value == "=SUM(F2:F2)"
    assert "Chưa có lịch" in workbook["Lịch Gantt"]["B2"].value
