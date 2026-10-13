from app.parsers.sample_profile import profile


def test_profile_reports_rows_types_empty_cells_and_pii():
    result = profile(
        [
            {"id": 1, "email": "fake@example.invalid", "phone": "0900000000"},
            {"id": 2, "email": "", "phone": None},
        ]
    )
    assert result["row_count"] == 2
    columns = {column["name"]: column for column in result["columns"]}
    assert columns["id"]["type"] == "number"
    assert columns["email"]["empty_pct"] == 50
    assert columns["email"]["pii_suspected"] is True
    assert result["readiness_suggestion"] in {"low", "medium", "high"}
