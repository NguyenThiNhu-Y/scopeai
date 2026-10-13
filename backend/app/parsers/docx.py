from io import BytesIO
def extract_text(data: bytes) -> str:
    try:
        from docx import Document
        return "\n".join(p.text for p in Document(BytesIO(data)).paragraphs)
    except Exception as exc: raise ValueError("Không đọc được DOCX — file hỏng") from exc
