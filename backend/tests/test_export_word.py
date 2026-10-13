from io import BytesIO

from docx import Document

from app.exporters.proposal_docx import render_proposal


def _data(locale="vi"):
    labels = {
        "introduction": "Giới thiệu",
        "solution_overview": "Tổng quan giải pháp",
        "approach": "Phương pháp",
        "risks": "Rủi ro",
        "conclusion": "Kết luận",
        "assumptions": "Giả định",
        "scope_out": "Ngoài phạm vi",
    }
    return {
        "project_name": "Dự án giả lập",
        "customer_name": "Khách hàng giả lập",
        "labels": labels,
        "sections": {"introduction": "Nội dung giả lập"},
        "assumptions": ["Giả định giả lập"],
        "scope_out": ["Ngoài phạm vi giả lập"],
        "quotation": "[Presales điền]",
    }


def test_word_opens_and_contains_cover_toc_and_sections():
    document = Document(BytesIO(render_proposal(_data())))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert "Dự án giả lập" in text
    assert "Mục lục" in text
    assert "Giả định" in text
    assert "Ngoài phạm vi" in text
    assert "[Presales điền]" in text
