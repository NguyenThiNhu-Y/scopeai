from app.parsers.requirements import normalize


def test_formula_code_is_replaced_and_codes_are_unique_across_sheets():
    sheets = {
        "A": [{"番号": "=ROW()-1", "機能要件": "Yêu cầu giả lập A"}],
        "B": [{"番号": "REQ-001", "機能要件": "Yêu cầu giả lập B"}],
    }
    rows = normalize(
        sheets,
        {sheet: {"code": "番号", "content": "機能要件"} for sheet in sheets},
    )
    codes = [row["internal_code"] for row in rows]
    assert len(codes) == 2
    assert len(codes) == len(set(codes))
    assert codes[0].startswith("REQ-")
    assert codes[0] != "=ROW()-1"
