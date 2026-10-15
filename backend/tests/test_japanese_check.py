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


def test_japanese_check_sends_masked_customer_name_and_section_context():
    """LLM phụ trợ phải nhận tên khách hàng đã mask + section nghi ngờ + glossary
    trong prompt (review M7 MEDIUM) — không chỉ {"customer_language": "ja"}."""

    class RecordingClient:
        def __init__(self):
            self.prompt = None
            self.context = None

        def complete(self, *, schema, prompt, context=None):
            self.prompt = prompt
            self.context = context
            return {"result": "pass", "issues": []}

    llm = RecordingClient()
    result = check_japanese(
        {"introduction": "株式会社デモ商事向けの提案です。連絡先 support@example.com"},
        "株式会社デモ商事（仮名・架空）",
        client=llm,
    )
    assert llm.prompt is not None, "có issue rule nên phải gọi LLM phụ trợ"
    assert "株式会社デモ商事" in llm.prompt
    assert "[introduction]" in llm.prompt
    assert "GLOSSARY" in llm.prompt
    assert "support@example.com" not in llm.prompt
    assert "[EMAIL]" in llm.prompt
    assert llm.context == {"customer_language": "ja"}
    assert result["result"] == "warning"
