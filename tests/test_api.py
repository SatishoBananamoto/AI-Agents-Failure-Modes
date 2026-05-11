from app.main import app, healthz, verify_endpoint
from app.schemas import VerifyRequest


def test_api_routes_registered():
    paths = {route.path for route in app.routes}
    assert "/healthz" in paths
    assert "/verify" in paths


def test_healthz():
    assert healthz() == {"status": "ok"}


def test_verify_endpoint_accepts_valid_payload():
    payload = {
        "session_id": "ICIF-AES-API-001",
        "as_of_date": "2026-05-02",
        "response_text": "[ICIF-AES Response Packet]\nTo: A\nFrom: B\nSession ID: ICIF-AES-API-001\nConversational State: TEST\nAnchor Points: A1\n\nBody.\n\nΔ-info: verification=yes",
        "claims": [],
        "evidence": [],
        "metadata": {"model_role": "verifier"},
    }

    result = verify_endpoint(VerifyRequest(**payload))
    assert result.pass_ is True
    assert result.violations == []
