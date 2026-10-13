from io import BytesIO
from openpyxl import Workbook


def render_estimate(data: dict) -> bytes:
    wb = Workbook(); summary = wb.active
    assert summary is not None
    summary.title = "Tóm tắt"
    summary.append(["Dự án", data["project_name"]]); summary.append(["Cổng giá", data["quotation"]])
    wbs = wb.create_sheet("WBS"); wbs.append(["Mã", "Tên", "Man-day"])
    for i in data["wbs"]: wbs.append([i.task_code, i.name_vi, i.man_day or 0])
    total_row = wbs.max_row + 1; wbs.cell(total_row, 2, "Tổng man-day"); wbs.cell(total_row, 3, f"=SUM(C2:C{total_row-1})")
    q = wb.create_sheet("Báo giá")
    q.append(["Hạng mục", "Số tiền"])
    q.append(["Giá trị trước duyệt", "[Presales điền]" if not data["approved"] else data["total"]])
    q.append(["Tổng", "=SUM(B2:B2)"])
    g = wb.create_sheet("Lịch Gantt"); g.append(["Tuần", "Task", "Mốc"])
    for row in data["schedule"]: g.append(row)
    qa = wb.create_sheet("Q&A"); qa.append(["Mã câu hỏi", "Vòng", "Câu hỏi", "Lý do tiếng Việt", "Ảnh hưởng", "Trả lời", "Là giả định", "Trạng thái"])
    for x in data["questions"]: qa.append([x.id, x.round_no, x.question, x.reason_vi, x.impact, x.answer or "", x.is_assumption, x.status])
    stream = BytesIO(); wb.save(stream); return stream.getvalue()
