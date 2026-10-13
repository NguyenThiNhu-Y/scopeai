def test_history_filters_by_customer_and_status(client):
    created = client.post(
        "/api/bids",
        json={
            "project_name": "Dự án lịch sử giả lập",
            "customer_name": "Khách hàng Lịch sử",
            "submission_deadline": "2026-12-20",
            "customer_language": "vi",
            "request_content": "Nội dung yêu cầu giả lập đủ dài cho bộ kiểm thử lịch sử.",
        },
    )
    assert created.status_code == 201
    changed = client.put(
        "/api/settings/factors",
        headers={"X-Actor": "manager_fixture"},
        json={"yaml_content": "factor_cap: 2\nfactors: {}", "by": "manager_fixture"},
    )
    assert changed.status_code == 200
    response = client.get("/api/history", params={"customer": "Lịch sử", "status": "draft"})
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["action"] == "update_reference"


def test_history_filters_by_bid_id(client):
    first = client.post(
        "/api/bids",
        json={
            "project_name": "Hồ sơ lịch sử một",
            "customer_name": "Khách hàng Một",
            "submission_deadline": "2026-12-20",
            "customer_language": "vi",
            "request_content": "Nội dung yêu cầu giả lập đủ dài cho lịch sử một.",
        },
    )
    assert first.status_code == 201
    first_id = first.json()["id"]

    response = client.put(
        "/api/settings/factors",
        headers={"X-Actor": "manager_fixture"},
        json={"yaml_content": "factor_cap: 2\nfactors: {}", "by": "manager_fixture"},
    )
    assert response.status_code == 200

    second = client.post(
        "/api/bids",
        json={
            "project_name": "Hồ sơ lịch sử hai",
            "customer_name": "Khách hàng Hai",
            "submission_deadline": "2026-12-20",
            "customer_language": "vi",
            "request_content": "Nội dung yêu cầu giả lập đủ dài cho lịch sử hai.",
        },
    )
    assert second.status_code == 201
    second_id = second.json()["id"]

    response = client.get("/api/history", params={"bid_id": first_id})
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["bid_id"] == first_id
    assert response.json()["items"][0]["bid_id"] != second_id
