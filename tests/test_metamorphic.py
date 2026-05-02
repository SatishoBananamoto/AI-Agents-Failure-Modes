from copy import deepcopy

from app.schemas import VerifyRequest
from app.verifier import verify


BASE = {
    "session_id": "ICIF-AES-MR-001",
    "as_of_date": "2026-05-02",
    "response_text": "[ICIF-AES Response Packet]\nTo: A\nFrom: B\nSession ID: ICIF-AES-MR-001\nConversational State: TEST\nAnchor Points: A1 Empirical Grounding\n\nBody.\n\nΔ-info: verification=yes",
    "claims": [
        {
            "claim_id": "C1",
            "text": "A factual claim with evidence.",
            "type": "factual",
            "confidence": "high",
            "evidence_ids": ["E1"],
            "time_sensitive": False,
        }
    ],
    "evidence": [
        {
            "evidence_id": "E1",
            "source_type": "spec",
            "url": "internal://x",
            "as_of_date": "2026-05-02",
            "supports_claim_ids": ["C1"],
        },
        {
            "evidence_id": "E2",
            "source_type": "tool",
            "url": "internal://disconfirmer-check",
            "as_of_date": "2026-05-02",
            "supports_claim_ids": ["C1"],
        },
    ],
    "disconfirmers": [
        {
            "disconfirmer_id": "D1",
            "claim_id": "C1",
            "text": "The factual claim would be weakened if its mapped evidence did not exist.",
            "check_type": "counterexample",
            "status": "checked_absent",
            "evidence_ids": ["E2"],
        }
    ],
    "metadata": {
        "model_role": "verifier",
        "requires_independent_derivation": False,
    },
}


def verdict(payload: dict) -> bool:
    return verify(VerifyRequest(**payload)).pass_


def test_whitespace_does_not_change_clean_verdict():
    mutated = deepcopy(BASE)
    mutated["response_text"] = "\n\n" + BASE["response_text"] + "\n\n"

    assert verdict(BASE) == verdict(mutated)


def test_claim_order_does_not_change_verdict():
    mutated = deepcopy(BASE)
    mutated["claims"] = list(reversed(BASE["claims"]))

    assert verdict(BASE) == verdict(mutated)


def test_unrelated_metadata_does_not_change_verdict():
    mutated = deepcopy(BASE)
    mutated["metadata"]["note"] = "non-verifier metadata should not affect v0.2 verdict"

    assert verdict(BASE) == verdict(mutated)
