from types import SimpleNamespace

from app.services.factor_engine import calculate_factors


def make_bid(**overrides):
    values = {
        "customer_language": "vi",
        "data_readiness": "ready",
        "no_requirement_file": False,
        "request_content": "simple request",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_no_factors_returns_identity_product():
    result = calculate_factors(make_bid())

    assert result["factors"] == []
    assert result["raw"] == 1.0
    assert result["product"] == 1.0


def test_japanese_and_unready_data_factors_are_applied():
    result = calculate_factors(
        make_bid(customer_language="ja", data_readiness="low", no_requirement_file=True)
    )

    assert [item["key"] for item in result["factors"]] == ["customer_jp", "data_not_ready"]
    assert result["raw"] == 1.56
    assert result["product"] == 1.56


def test_many_factors_are_capped_once():
    result = calculate_factors(
        make_bid(
            customer_language="ja",
            data_readiness="low",
            no_requirement_file=True,
            request_content=(
                "on-premise compliance multi đa ngôn ngữ ocr million requirement"
            ),
        )
    )

    assert result["raw"] > result["cap"]
    assert result["product"] == result["cap"]


def test_requirement_factor_uses_actual_count_not_email_words():
    bid = make_bid(request_content="email có chữ requirement nhưng chỉ một yêu cầu")
    bid.id = 1
    class Session:
        def query(self, model):
            return self
        def filter_by(self, **kwargs):
            return self
        def count(self):
            return 30
    result = calculate_factors(bid, Session())
    assert [item["key"] for item in result["factors"]] == ["many_requirements"]
