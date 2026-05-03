from copy import deepcopy

from app.schemas import VerifyRequest
from app.verifier import verify


BASE = {
    "session_id": "ICIF-AES-DISC-TEST",
    "as_of_date": "2026-05-02",
    "response_text": "[ICIF-AES Response Packet]\nTo: A\nFrom: B\nSession ID: ICIF-AES-DISC-TEST\nConversational State: TEST\nAnchor Points: A1 Empirical Grounding\n\nAll relevant tests passed.\n\nΔ-info: verification=yes",
    "claims": [
        {
            "claim_id": "C1",
            "text": "All relevant tests passed.",
            "type": "factual",
            "confidence": "high",
            "evidence_ids": ["E1"],
            "time_sensitive": False,
        }
    ],
    "evidence": [
        {
            "evidence_id": "E1",
            "source_type": "tool",
            "url": "internal://test-run",
            "quote": "All relevant tests passed.",
            "as_of_date": "2026-05-02",
            "supports_claim_ids": ["C1"],
        },
        {
            "evidence_id": "E2",
            "source_type": "tool",
            "url": "internal://disconfirmer-check",
            "quote": "No later relevant failing test run was found in this fixture.",
            "as_of_date": "2026-05-02",
            "supports_claim_ids": ["C1"],
        },
    ],
    "disconfirmers": [
        {
            "disconfirmer_id": "D1",
            "claim_id": "C1",
            "text": "A later relevant test run fails after the claimed passing run.",
            "check_type": "tool_result",
            "status": "checked_absent",
            "evidence_ids": ["E2"],
        }
    ],
    "metadata": {"model_role": "verifier"},
}


def result_for(payload: dict):
    return verify(VerifyRequest(**payload))


def test_checked_absent_disconfirmer_allows_high_confidence_factual_claim():
    result = result_for(BASE)
    assert result.pass_ is True
    assert result.violations == []


def test_missing_disconfirmer_fails_high_confidence_factual_claim():
    payload = deepcopy(BASE)
    payload["disconfirmers"] = []

    result = result_for(payload)

    assert result.pass_ is False
    assert any(v.rule_id == "DISCONFIRMER_REQUIRED" for v in result.violations)


def test_unchecked_disconfirmer_fails():
    payload = deepcopy(BASE)
    payload["disconfirmers"][0]["status"] = "not_checked"

    result = result_for(payload)

    assert result.pass_ is False
    assert any(v.rule_id == "DISCONFIRMER_UNCHECKED" for v in result.violations)


def test_present_disconfirmer_fails():
    payload = deepcopy(BASE)
    payload["disconfirmers"][0]["status"] = "checked_present"

    result = result_for(payload)

    assert result.pass_ is False
    assert any(v.rule_id == "DISCONFIRMER_PRESENT" for v in result.violations)


def test_vague_disconfirmer_fails():
    payload = deepcopy(BASE)
    payload["disconfirmers"][0]["text"] = "Maybe something could be wrong"

    result = result_for(payload)

    assert result.pass_ is False
    assert any(v.rule_id == "DISCONFIRMER_INVALID" for v in result.violations)


def test_orphan_disconfirmer_fails():
    payload = deepcopy(BASE)
    payload["disconfirmers"][0]["claim_id"] = "C404"

    result = result_for(payload)

    assert result.pass_ is False
    assert any(v.rule_id == "DISCONFIRMER_ORPHAN" for v in result.violations)


def test_disconfirmer_missing_evidence_fails():
    payload = deepcopy(BASE)
    payload["disconfirmers"][0]["evidence_ids"] = ["E404"]

    result = result_for(payload)

    assert result.pass_ is False
    assert any(v.rule_id == "DISCONFIRMER_EVIDENCE_MISSING" for v in result.violations)
