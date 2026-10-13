from io import BytesIO

import openpyxl

from app.parsers.excel import read_sheets


def test_excel_reader_reads_all_sheets():
    wb = openpyxl.Workbook()
    first = wb.worksheets[0]
    first.title = "Requirements"
    first.append(["code", "content", "priority"])
    first.append(["REQ-001", "Dữ liệu giả lập", "mandatory"])
    second = wb.create_sheet("Additional")
    second.append(["code", "content", "priority"])
    second.append(["REQ-002", "Báo cáo giả lập", "optional"])
    stream = BytesIO()
    wb.save(stream)

    sheets = read_sheets(stream.getvalue(), "requirements.xlsx")
    assert set(sheets) == {"Requirements", "Additional"}
    assert len(sheets["Requirements"]) == 1
    assert len(sheets["Additional"]) == 1
