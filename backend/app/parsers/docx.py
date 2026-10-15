from io import BytesIO


def extract_text(data: bytes) -> str:
    """Trích văn bản DOCX: đoạn văn + bảng, giữ đúng thứ tự xuất hiện.

    Mỗi dòng bảng nối các ô bằng " | " (giữ thứ tự cột); dòng bảng xen kẽ
    với đoạn văn theo đúng thứ tự trong tài liệu. Bỏ dòng rỗng.
    """
    try:
        from docx import Document
        from docx.table import Table
        from docx.text.paragraph import Paragraph

        doc = Document(BytesIO(data))
        parts: list[str] = []
        for block in doc.iter_inner_content():
            if isinstance(block, Paragraph):
                if block.text.strip():
                    parts.append(block.text)
            elif isinstance(block, Table):
                for row in block.rows:
                    cells = [cell.text.strip() for cell in row.cells]
                    parts.append(" | ".join(cells))
        return "\n".join(parts)
    except Exception as exc:
        raise ValueError("Không đọc được DOCX — file hỏng") from exc