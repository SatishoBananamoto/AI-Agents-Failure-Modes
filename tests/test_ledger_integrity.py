from copy import deepcopy

from app.schemas import VerifyRequest
from app.verifier import verify


BASE = {
    "session_id": "ICIF-AES-LEDGER-TEST",
    "as_of_date": "2026-05-02",
    "response_text": "[ICIF-AES Response Packet]\nTo: A\nFrom: B\nSession ID: ICIF-AES-LEDGER-TEST\nConversational State: TEST\nAnchor Points: A1 Empirical Grounding\n\nAll relevant tests passed.\n\nΔ-info: verification=yes",
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


def test_clean_ledger_passes():
    result = result_for(BASE)
    assert result.pass_ is True
    assert result.violations == []


def test_response_assertion_missing_from_claim_ledger_fails():
    payload = deepcopy(BASE)
    payload["response_text"] = (
        "[ICIF-AES Response Packet]\nTo: A\nFrom: B\nSession ID: ICIF-AES-LEDGER-TEST\n"
        "Conversational State: TEST\nAnchor Points: A1 Empirical Grounding\n\n"
        "All relevant tests passed. The system is secure. No secrets leaked.\n\n"
        "Δ-info: verification=yes"
    )

    result = result_for(payload)

    assert result.pass_ is False
    assert any(v.rule_id == "LEDGER_MISSING_CLAIMS" for v in result.violations)


def test_claim_not_grounded_in_response_fails():
    payload = deepcopy(BASE)
    payload["response_text"] = (
        "[ICIF-AES Response Packet]\nTo: A\nFrom: B\nSession ID: ICIF-AES-LEDGER-TEST\n"
        "Conversational State: TEST\nAnchor Points: A1 Empirical Grounding\n\n"
        "Only formatting was discussed.\n\n"
        "Δ-info: verification=yes"
    )

    result = result_for(payload)

    assert result.pass_ is False
    assert any(v.rule_id == "LEDGER_CLAIM_NOT_IN_RESPONSE" for v in result.violations)


def test_factual_language_hidden_as_speculation_fails():
    payload = deepcopy(BASE)
    payload["claims"] = [
        {
            "claim_id": "C1",
            "text": "All relevant tests passed.",
            "type": "speculation",
            "confidence": "low",
            "evidence_ids": [],
            "time_sensitive": False,
        }
    ]
    payload["evidence"] = []
    payload["disconfirmers"] = []

    result = result_for(payload)

    assert result.pass_ is False
    assert any(v.rule_id == "LEDGER_TYPE_MISCLASSIFICATION" for v in result.violations)


def test_claim_supporting_evidence_without_quote_fails():
    payload = deepcopy(BASE)
    payload["evidence"][0].pop("quote")

    result = result_for(payload)

    assert result.pass_ is False
    assert any(v.rule_id == "EVIDENCE_WITHOUT_QUOTE" for v in result.violations)


def test_weak_self_attested_evidence_fails():
    payload = deepcopy(BASE)
    payload["evidence"][0]["source_type"] = "internal"

    result = result_for(payload)

    assert result.pass_ is False
    assert any(v.rule_id == "EVIDENCE_SELF_ATTESTED" for v in result.violations)


def test_claim_supporting_evidence_without_url_fails():
    payload = deepcopy(BASE)
    payload["evidence"][0]["url"] = None

    result = result_for(payload)

    assert result.pass_ is False
    assert any(v.rule_id == "SOURCE_NOT_VERIFIABLE" for v in result.violations)
