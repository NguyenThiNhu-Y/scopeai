from app.parsers.detect import detect_type
from app.parsers.text import extract_text
from app.parsers.pdf import extract_text as extract_pdf_text
from app.parsers.docx import extract_text as extract_docx_text
from app.parsers.excel import read_sheets
from app.parsers.sample_profile import profile
from datetime import date
import pytest

from app.services.attachment_service import add
from app.api.errors import ApiError
from app.core import db
from app.models import Bid


def test_file_reader_supports_text_and_rejects_unknown_extension():
    assert extract_text("DỮ LIỆU GIẢ LẬP\nYêu cầu CRM".encode()) == "DỮ LIỆU GIẢ LẬP\nYêu cầu CRM"
    assert detect_type("rfp.txt", b"text") == "rfp"

    with pytest.raises(ValueError, match="không được hỗ trợ"):
        detect_type("malware.exe", b"not executable")


def test_csv_detection_distinguishes_fault_history_from_requirements():
    assert detect_type("requirements_tokai.csv", b"No,Requirement\nR-1,Login") == "requirement"
    assert detect_type("fault_history_tokai.csv", b"date,equipment\n2026-01-01,MC-850H") == "sample_data"
    assert detect_type(
        "別紙2_故障履歴サンプル_2025-2026.csv",
        "発生日,設備\n2026-01-01,MC-850H".encode(),
    ) == "sample_data"


def test_tokai_minato_fixture_set_is_parseable():
    from pathlib import Path

    tokai_dir = Path(__file__).resolve().parents[2] / "sample_data" / "rfp_tokai_minato"
    real_dir = tokai_dir / "real"
    request_text = (tokai_dir / "email_yeu_cau_khach.txt").read_bytes()
    assert "設備保全ナレッジAIアシスタント" in extract_text(request_text)
    assert "2026年10月30日" in extract_text(request_text)

    rfp_docx = next(real_dir.glob("*.docx"))
    assert "設備保全" in extract_docx_text(rfp_docx.read_bytes())

    # DOCX đọc cả bảng: dòng bảng nối các ô bằng " | ", giữ thứ tự tài liệu.
    docx_text = extract_docx_text(rfp_docx.read_bytes())
    assert "Phase 2：本開発 | 2027年4月〜2027年9月" in docx_text
    assert "Phase 3：展開・運用 | 2027年10月〜" in docx_text

    manual_pdf = next(real_dir.glob("*.pdf"))
    assert "MC-850H" in extract_pdf_text(manual_pdf.read_bytes())

    requirements_xlsx = next(real_dir.glob("*.xlsx"))
    requirements = read_sheets(requirements_xlsx.read_bytes(), requirements_xlsx.name)
    assert {"機能要件", "非機能要件"} <= set(requirements)
    assert any("多言語" in str(row) for rows in requirements.values() for row in rows)

    history_csv = next(real_dir.glob("*.csv"))
    history = read_sheets(history_csv.read_bytes(), history_csv.name)
    summary = profile(history["CSV"])
    assert summary["row_count"] == 600
    assert any(column["name"] == "対応者メール" and column["pii_suspected"] for column in summary["columns"])


def test_pdf_with_text_layer_is_extracted():
    """Regression: pypdf phải có trong requirements.txt — nếu thiếu, mọi PDF
    bị đánh dấu lỗi 'không có lớp chữ' và chặn confirm (409)."""
    from io import BytesIO

    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(72, 750, "MC-850H manual page")
    pdf.showPage()
    pdf.save()

    text = extract_pdf_text(buffer.getvalue())
    assert "MC-850H manual page" in text


def test_upload_rejects_path_traversal_and_unknown_file_type():
    session = db.SessionLocal()
    bid = Bid(
        project_name="Test", customer_name="Fake", submission_deadline=date(2026, 12, 1),
        customer_language="vi", request_content="Fake", created_by="test",
    )
    session.add(bid)
    session.commit()
    try:
        for filename in ("../escape.txt", "nested/escape.txt"):
            try:
                add(session, bid.id, filename, b"ok")
            except ApiError as exc:
                assert exc.code == "INVALID_FILE_TYPE"
            else:
                raise AssertionError("unsafe filename must be rejected")
        try:
            add(session, bid.id, "requirements.csv", b"content\nCRM", "not-a-type")
        except ApiError as exc:
            assert exc.code == "INVALID_FILE_TYPE"
        else:
            raise AssertionError("unknown file type must be rejected")
    finally:
        session.close()


def test_upload_size_error_uses_frozen_contract_status():
    session = db.SessionLocal()
    bid = Bid(
        project_name="Test", customer_name="Fake", submission_deadline=date(2026, 12, 1),
        customer_language="vi", request_content="Fake", created_by="test",
    )
    session.add(bid)
    session.commit()
    try:
        with pytest.raises(ApiError) as error:
            add(session, bid.id, "requirements.txt", b"x" * (20 * 1024 * 1024 + 1))
        assert error.value.status_code == 400
        assert error.value.code == "FILE_TOO_LARGE"
    finally:
        session.close()
