def read_sheets(data: bytes, filename: str) -> dict:
    """Đọc XLS legacy nếu xlrd có mặt; không tạo requirement giả khi thiếu thư viện."""
    try:
        import xlrd
        book = xlrd.open_workbook(file_contents=data)
        return {sheet.name: [dict(zip(sheet.row_values(0), [c.value for c in row])) for row in list(sheet.get_rows())[1:]] for sheet in book.sheets() if sheet.nrows}
    except ImportError as exc:
        raise ValueError("Không đọc được XLS — vui lòng lưu lại dưới dạng XLSX") from exc
    except Exception as exc:
        raise ValueError("Không đọc được XLS — file hỏng hoặc cần lưu lại dưới dạng XLSX") from exc
