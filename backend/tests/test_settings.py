import yaml


def test_settings_returns_repo_tables(client):
    response = client.get("/api/settings")
    assert response.status_code == 200
    body = response.json()
    keys = {item["key"] for item in body["keys"]}
    assert {"effort", "rate_card", "factors"} <= keys
    assert {"company", "templates", "standard_content", "case_studies", "bid_no_bid"} <= keys
    assert all(item["source"] == "repo" for item in body["keys"])
    payloads = {item["key"]: item["payload"] for item in body["keys"]}
    assert set(payloads["effort"]["directions"]) == {"none", "traditional_ml", "rag", "agent", "fine_tune"}
    assert set(payloads["rate_card"]["rates"]) == {"pm", "ba", "brse", "ai_engineer", "backend", "frontend", "qa", "infra"}
    assert payloads["factors"]["factor_cap"] > 1


def test_manager_can_update_effort_and_new_effort_uses_override(client):
    original = client.get("/api/settings").json()["keys"][0]["yaml_preview"]
    payload = yaml.safe_load(original)
    payload["directions"]["none"]["poc"]["min"] = 3
    response = client.put(
        "/api/settings/effort",
        headers={"X-Actor": "manager"},
        json={"yaml_content": yaml.safe_dump(payload), "by": "manager_fixture"},
    )
    assert response.status_code == 200
    assert response.json()["source"] == "db"
    assert client.get("/api/settings").json()["keys"][0]["source"] == "db"


def test_any_single_mvp_user_can_update_settings(client):
    response = client.put(
        "/api/settings/factors",
        json={"yaml_content": "factor_cap: 2", "by": "presales"},
    )
    assert response.status_code == 200
