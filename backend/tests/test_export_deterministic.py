from types import SimpleNamespace

from app.exporters.bundle import make_bundle
from app.exporters.estimate_xlsx import render_estimate
from app.exporters.filename import export_filename


def test_bundle_bytes_and_entry_order_are_deterministic():
    files = [("proposal.docx", b"docx"), ("estimate.xlsx", b"xlsx"), ("proposal.pdf", b"pdf")]
    assert make_bundle(files) == make_bundle(files)


def test_filename_is_safe_and_stable():
    name = export_filename("Khách/giả lập", "Dự án: thử", "proposal", export_date="2026-10-10", ext="docx")
    assert name == "Khách-giả-lập_Dự-án-thử_proposal_v1_2026-10-10.docx"
    assert "/" not in name and "\\" not in name
