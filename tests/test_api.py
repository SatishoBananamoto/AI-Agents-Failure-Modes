from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_verify_endpoint_accepts_valid_payload():
    payload = {
        "session_id": "ICIF-AES-API-001",
        "as_of_date": "2026-05-02",
        "response_text": "[ICIF-AES Response Packet]\nTo: A\nFrom: B\nSession ID: ICIF-AES-API-001\nConversational State: TEST\nAnchor Points: A1\n\nBody.\n\nΔ-info: verification=yes",
        "claims": [],
        "evidence": [],
        "metadata": {"model_role": "verifier"},
    }

    response = client.post("/verify", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["pass"] is True
    assert body["violations"] == []
