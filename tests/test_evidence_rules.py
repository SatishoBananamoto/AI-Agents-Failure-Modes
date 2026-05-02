from app.rules.evidence import check_evidence
from app.schemas import VerifyRequest


def test_missing_evidence_id_is_fm1():
    req = VerifyRequest(
        session_id="ICIF-AES-EVIDENCE-TEST",
        as_of_date="2026-05-02",
        response_text="[ICIF-AES Response Packet]\nTo: A\nFrom: B\nSession ID: ICIF-AES-EVIDENCE-TEST\nConversational State: TEST\nAnchor Points: A1\n\nBody.\n\nΔ-info: verification=yes",
        claims=[
            {
                "claim_id": "C1",
                "text": "Claim references missing evidence.",
                "type": "factual",
                "confidence": "medium",
                "evidence_ids": ["E404"],
            }
        ],
        evidence=[],
        metadata={"model_role": "verifier"},
    )

    violations = check_evidence(req)
    assert any(v.rule_id == "FM1" and "E404" in v.message for v in violations)


def test_evidence_support_claim_mapping_is_checked():
    req = VerifyRequest(
        session_id="ICIF-AES-EVIDENCE-TEST-2",
        as_of_date="2026-05-02",
        response_text="[ICIF-AES Response Packet]\nTo: A\nFrom: B\nSession ID: ICIF-AES-EVIDENCE-TEST-2\nConversational State: TEST\nAnchor Points: A1\n\nBody.\n\nΔ-info: verification=yes",
        claims=[
            {
                "claim_id": "C1",
                "text": "Claim mapped to evidence that supports another claim.",
                "type": "factual",
                "confidence": "medium",
                "evidence_ids": ["E1"],
            }
        ],
        evidence=[
            {
                "evidence_id": "E1",
                "source_type": "spec",
                "url": "internal://fixture",
                "as_of_date": "2026-05-02",
                "supports_claim_ids": ["C2"],
            }
        ],
        metadata={"model_role": "verifier"},
    )

    violations = check_evidence(req)
    assert any(v.rule_id == "FM1" and v.severity == 2 for v in violations)
