from zipfile import ZipFile
from io import BytesIO

from app.exporters.bundle import make_bundle


def test_bundle_contains_exactly_three_artifacts_without_path_leak():
    payload = make_bundle([
        ("customer_project_proposal_v1_2026-10-10.docx", b"docx"),
        ("customer_project_estimate_v1_2026-10-10.xlsx", b"xlsx"),
        ("customer_project_proposal_v1_2026-10-10.pdf", b"pdf"),
    ])
    with ZipFile(BytesIO(payload)) as archive:
        assert archive.namelist() == [
            "customer_project_proposal_v1_2026-10-10.docx",
            "customer_project_estimate_v1_2026-10-10.xlsx",
            "customer_project_proposal_v1_2026-10-10.pdf",
        ]
        assert all("/" not in name and "\\" not in name for name in archive.namelist())
