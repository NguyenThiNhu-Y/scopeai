from types import SimpleNamespace

from app.services.effort_engine import calculate_effort


def make_bid(**overrides):
    values = {
        "customer_language": "ja",
        "data_readiness": "low",
        "no_requirement_file": True,
        "request_content": "requirement dữ liệu lớn",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_effort_has_all_phases_and_is_capped():
    result = calculate_effort(make_bid(), "rag")

    assert set(result["by_phase"]) == {"poc", "mvp", "production"}
    assert result["factor_product"] <= result["cap"]
    assert result["trace"]["raw_factor_product"] > result["trace"]["capped_factor_product"]


def test_effort_changes_by_direction_without_llm():
    bid = make_bid()

    assert calculate_effort(bid, "rag")["midpoint_total"] != calculate_effort(bid, "none")["midpoint_total"]


def test_rag_reference_range_matches_medium_enterprise_fixture():
    result = calculate_effort(make_bid(customer_language="vi", data_readiness="ready", no_requirement_file=False, request_content="simple request"), "rag")
    assert result["by_phase"]["poc"] == {"min": 40.0, "max": 60.0}
    assert result["by_phase"]["mvp"] == {"min": 150.0, "max": 220.0}
    assert result["by_phase"]["production"] == {"min": 60.0, "max": 100.0}


def test_every_direction_has_mvp_larger_than_poc_and_production():
    from app.services.reference_service import load_effort

    for phases in load_effort()["directions"].values():
        assert phases["mvp"]["min"] > phases["poc"]["max"]
        assert phases["mvp"]["min"] > phases["production"]["max"]


def test_effort_single_factor_has_deterministic_trace():
    result = calculate_effort(
        make_bid(data_readiness="ready", no_requirement_file=False, request_content="simple request"),
        "none",
    )

    assert result["factor_product"] == 1.2
    assert result["trace"]["raw_factor_product"] == 1.2
    assert result["trace"]["capped_factor_product"] == 1.2
