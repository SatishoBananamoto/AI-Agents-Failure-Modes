from app.rules.protocol import check_protocol
from app.schemas import VerifyRequest


def make_request(response_text: str) -> VerifyRequest:
    return VerifyRequest(
        session_id="ICIF-AES-PROTO-TEST",
        as_of_date="2026-05-02",
        response_text=response_text,
        claims=[],
        evidence=[],
        metadata={"model_role": "verifier"},
    )


def test_protocol_accepts_complete_packet():
    req = make_request(
        "[ICIF-AES Response Packet]\n"
        "To: A\n"
        "From: B\n"
        "Session ID: ICIF-AES-PROTO-TEST\n"
        "Conversational State: TEST\n"
        "Anchor Points: A1 Empirical Grounding\n\n"
        "Body.\n\n"
        "Δ-info: verification=yes"
    )

    assert check_protocol(req) == []


def test_protocol_flags_missing_delta_footer():
    req = make_request(
        "[ICIF-AES Response Packet]\n"
        "To: A\n"
        "From: B\n"
        "Session ID: ICIF-AES-PROTO-TEST\n"
        "Conversational State: TEST\n"
        "Anchor Points: A1 Empirical Grounding\n\n"
        "Body."
    )

    violations = check_protocol(req)
    assert any(v.rule_id == "PROTO_DELTA" for v in violations)
