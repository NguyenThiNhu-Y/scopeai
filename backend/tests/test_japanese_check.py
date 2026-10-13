from app.services.ja_check import check_japanese


def test_japanese_check_passes_clean_customer_text():
    result = check_japanese({"introduction": "株式会社デモ商事（仮名・架空）向けの提案です。"}, "株式会社デモ商事（仮名・架空）")
    assert result == {"result": "pass", "issues": []}


def test_japanese_check_warns_latin_glossary_and_missing_name():
    result = check_japanese({"introduction": "proposal system API"}, "株式会社デモ商事（仮名・架空）")
    assert result["result"] == "warning"
    assert {issue["source"] for issue in result["issues"]} >= {"latin", "glossary", "name"}


def test_japanese_check_keeps_rule_warning_when_llm_schema_is_invalid():
    class BadClient:
        def complete(self, *_args, **_kwargs):
            return {"invalid": True}

    result = check_japanese({"introduction": "unknownterm"}, "顧客", client=BadClient())
    assert result["result"] == "warning"
    assert result["issues"]
