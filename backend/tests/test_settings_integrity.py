def test_invalid_effort_keeps_repo_value(client):
    response = client.put(
        "/api/settings/effort",
        headers={"X-Role": "manager"},
        json={"yaml_content": "directions: {}", "by": "manager_fixture"},
    )
    assert response.status_code == 400
    assert "giữ nguyên" in response.json()["error"]["message"]
    assert client.get("/api/settings").json()["keys"][0]["source"] == "repo"


def test_invalid_rate_card_reports_missing_roles(client):
    response = client.put(
        "/api/settings/rate_card",
        headers={"X-Role": "manager"},
        json={"yaml_content": "rates: {pm: {offshore: 1, onsite: 1}}", "by": "manager_fixture"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["details"]["errors"]


def test_factor_cap_must_be_above_one(client):
    response = client.put(
        "/api/settings/factors",
        headers={"X-Role": "manager"},
        json={"yaml_content": "factor_cap: 1", "by": "manager_fixture"},
    )
    assert response.status_code == 400
