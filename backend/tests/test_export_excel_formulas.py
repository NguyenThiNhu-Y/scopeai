from io import BytesIO
from types import SimpleNamespace

import openpyxl

from app.exporters.estimate_xlsx import render_estimate


def test_excel_has_required_sheets_formulas_gantt_and_qna():
    data = {
        "project_name": "Dự án giả lập",
        "quotation": "[Presales điền]",
        "approved": False,
        "total": None,
        "wbs": [SimpleNamespace(task_code="1.1", name_vi="Thiết kế giả lập", man_day=2)],
        "schedule": [["W01", "Thiết kế giả lập", ""]],
        "questions": [SimpleNamespace(id=1, round_no=1, question="Câu hỏi giả lập", reason_vi="Lý do", impact="solution", answer=None, is_assumption=False, status="awaiting_answer")],
    }
    workbook = openpyxl.load_workbook(BytesIO(render_estimate(data)), data_only=False)
    assert workbook.sheetnames == ["Tóm tắt", "WBS", "Báo giá", "Lịch Gantt", "Q&A"]
    assert workbook["WBS"]["C3"].value == "=SUM(C2:C2)"
    assert workbook["Báo giá"]["B3"].value == "=SUM(B2:B2)"
    assert workbook["Lịch Gantt"]["A2"].value == "W01"
    assert workbook["Q&A"]["C2"].value == "Câu hỏi giả lập"
