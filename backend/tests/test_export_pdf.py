from app.exporters.pdf import docx_to_pdf
from app.exporters.proposal_docx import render_proposal


def test_pdf_export_has_fallback_when_libreoffice_is_unavailable(monkeypatch):
    monkeypatch.setattr("app.exporters.pdf.shutil.which", lambda _: None)
    payload = render_proposal({
        "project_name": "Dự án giả lập",
        "customer_name": "Khách hàng giả lập",
        "labels": {"toc": "Mục lục"},
        "sections": {"introduction": "Nội dung giả lập"},
        "quotation": "[Presales điền]",
    })

    pdf = docx_to_pdf(payload)

    assert pdf.startswith(b"%PDF-")
