from io import BytesIO
def extract_text(data: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError("Không đọc được PDF — thiếu thư viện pypdf") from exc
    try:
        return "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(data)).pages)
    except Exception as exc:
        raise ValueError("Không đọc được PDF — file hỏng hoặc không có lớp chữ") from exc