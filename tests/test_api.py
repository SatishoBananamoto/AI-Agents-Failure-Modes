from app.main import app, healthz, verify_endpoint, verify_session_endpoint
from app.schemas import VerifyRequest
from app.session_schemas import SessionVerifyRequest


def test_api_routes_registered():
    paths = {route.path for route in app.routes}
    assert "/healthz" in paths
    assert "/verify" in paths
    assert "/verify-session" in paths


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


def test_verify_session_endpoint_accepts_raw_session_payload():
    payload = {
        "session_id": "ICIF-AES-SESSION-API-001",
        "as_of_date": "2026-05-12",
        "messages": [
            {
                "role": "tool",
                "event_type": "tool_result",
                "name": "pytest",
                "content": "3 passed",
                "metadata": {"exit_code": 0},
            },
            {
                "role": "assistant",
                "content": "Tests passed.",
            },
        ],
    }

    result = verify_session_endpoint(SessionVerifyRequest(**payload))

    assert result.pass_ is True
    assert result.violations == []
