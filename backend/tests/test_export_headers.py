from app.api.routers.exports import _response


def test_export_content_disposition_supports_unicode_filename(client, monkeypatch):
    class Bid:
        customer_name = "Khách hàng"
        project_name = "Dự án"
        customer_language = "vi"

    monkeypatch.setattr(
        "app.api.routers.exports.artifacts",
        lambda *args: (Bid(), False, {"result": "pass", "issues": []}, {"docx": ("Khách hàng_Dự án_proposal.docx", b"docx")}),
    )
    monkeypatch.setattr("app.api.routers.exports.log_export", lambda *args: None)

    response = _response(object(), 1, "docx", "tester", "application/octet-stream")

    disposition = response.headers["content-disposition"]
    assert "filename=\"Khach-hang_Du-an_proposal.docx\"" in disposition
    assert "filename*=UTF-8''Kh%C3%A1ch%20h%C3%A0ng_D%E1%BB%B1%20%C3%A1n_proposal.docx" in disposition
