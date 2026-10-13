from tests.helpers import create_bid


def test_settings_expose_dot9_tabs(client):
    response = client.get("/api/settings")
    assert response.status_code == 200
    keys = {item["key"] for item in response.json()["keys"]}
    assert {"company", "templates", "standard_content", "case_studies", "bid_no_bid"} <= keys


def test_bid_no_bid_requires_weighted_criteria_and_records_confirmation(client):
    bid_id = create_bid(client, project_name="Dự án mẫu")
    response = client.put(f"/api/bids/{bid_id}/bid-qualification", json={
        "decision": "bid",
        "confirmer": "presales-demo",
        "criteria": [
            {"id": "fit", "label_vi": "Phù hợp", "weight": 60, "score": 4},
            {"id": "delivery", "label_vi": "Triển khai", "weight": 40, "score": 3},
        ],
    })
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "bid"
    assert body["confirmer"] == "presales-demo"
    assert len(body["suggestions"]) == 2


def test_bid_no_bid_rejects_invalid_weight_total(client):
    bid_id = create_bid(client, project_name="Dự án mẫu")
    response = client.put(f"/api/bids/{bid_id}/bid-qualification", json={
        "criteria": [{"id": "fit", "label_vi": "Phù hợp", "weight": 90}],
    })
    assert response.status_code == 400


def test_proposal_translation_and_document_metadata(client):
    bid_id = create_bid(client, project_name="Dự án mẫu")
    proposal = client.get(f"/api/bids/{bid_id}/proposal")
    assert proposal.status_code == 200
    assert proposal.json()["document"] == {"page_size": "A4", "cover": True, "table_of_contents": list(proposal.json()["sections"]), "printable": True}
    response = client.post(f"/api/bids/{bid_id}/proposal/translate", json={"language": "en", "sections": {key: f"Translated {key}" for key in proposal.json()["sections"]}})
    assert response.status_code == 200
    assert "en" in response.json()["translations"]


def test_proposal_versions_progress_and_sent_history(client):
    bid_id = create_bid(client, project_name="Dự án mẫu")
    first = client.post(f"/api/bids/{bid_id}/proposal/versions", json={"by": "presales-demo", "language": "en"})
    assert first.status_code == 201
    assert first.json()["version"] == "1.0"
    sent = client.put(f"/api/bids/{bid_id}/proposal/versions/{first.json()['id']}/sent", json={"note": "Đã gửi bản chào giá qua email"}, headers={"X-Actor": "presales-demo"})
    assert sent.status_code == 200
    assert sent.json()["sent"] is True
    assert sent.json()["sent_at"] is not None
    assert sent.json()["sent_note"] == "Đã gửi bản chào giá qua email"
    history = client.get(f"/api/history?bid_id={bid_id}")
    assert any(item["action"] == "send_proposal" for item in history.json()["items"])


def test_proposal_versions_follow_requested_progression(client):
    bid_id = create_bid(client, project_name="Dự án mẫu")
    first = client.post(f"/api/bids/{bid_id}/proposal/versions", json={"by": "presales-demo"})
    second = client.post(f"/api/bids/{bid_id}/proposal/versions", json={"by": "presales-demo"})
    third = client.post(f"/api/bids/{bid_id}/proposal/versions", json={"by": "presales-demo"})
    assert [first.json()["version"], second.json()["version"], third.json()["version"]] == ["1.0", "1.1", "2.0"]


def test_deal_stage_update_is_audited(client):
    bid_id = create_bid(client, project_name="Dự án mẫu")
    response = client.put(f"/api/bids/{bid_id}/deal-stage", json={"deal_stage": "negotiation", "note": "Khách đang đánh giá"}, headers={"X-Actor": "presales-demo"})
    assert response.status_code == 200
    assert response.json()["deal_stage"] == "negotiation"
    history = client.get(f"/api/history?bid_id={bid_id}")
    assert history.json()["items"][0]["action"] == "update_deal_stage"
