from io import BytesIO
from types import SimpleNamespace

import openpyxl

from app.exporters.estimate_xlsx import render_estimate


def test_unapproved_excel_uses_placeholder_not_real_amount():
    workbook = openpyxl.load_workbook(BytesIO(render_estimate({
        "project_name": "Dự án giả lập",
        "quotation": "[Presales điền]",
        "approved": False,
        "total": 123456,
        "wbs": [],
        "schedule": [],
        "questions": [],
    })), data_only=False)
    assert workbook["Tóm tắt"]["B2"].value == "[Presales điền]"
    assert workbook["Báo giá"]["B2"].value == "[Presales điền]"
    assert "123456" not in " ".join(str(cell.value) for row in workbook["Báo giá"].iter_rows() for cell in row)
