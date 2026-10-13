from types import SimpleNamespace

from app.services.effort_engine import calculate_effort


def test_effort_trace_preserves_reference_provenance():
    bid = SimpleNamespace(
        customer_language="ja",
        data_readiness="low",
        no_requirement_file=True,
        request_content="requirement dữ liệu lớn",
    )

    result = calculate_effort(bid, "rag")
    trace = result["trace"]

    assert trace["table_version"] == 5
    assert trace["source"] == "reference/effort.yaml + context hồ sơ"
    assert trace["formula"] == "Σ midpoint(min,max) × factor_product"
    assert trace["raw_factor_product"] >= trace["capped_factor_product"]
    assert len(result["factors"]) >= 1
