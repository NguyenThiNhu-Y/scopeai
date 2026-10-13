from app.parsers.requirements import normalize


def test_duplicate_source_codes_get_unique_internal_codes():
    rows = normalize(
        {"CSV": [
            {"code": "REQ-001", "content": "Yêu cầu giả lập 1"},
            {"code": "REQ-001", "content": "Yêu cầu giả lập 2"},
            {"code": "", "content": "Yêu cầu giả lập 3"},
        ]},
        {"CSV": {"code": "code", "content": "content"}},
    )
    codes = [row["internal_code"] for row in rows]
    assert len(codes) == 3
    assert len(codes) == len(set(codes))
