"""Ledger integrity checks for ICIF-AES verifier v0.3.

These checks treat the claim/evidence ledger as untrusted input. They do not try to
solve full semantic entailment; they enforce hard, deterministic integrity rules
that catch common ways an LLM can hide or weaken claims in JSON.
"""

from __future__ import annotations

import re
from collections import defaultdict

from app.schemas import VerifyRequest, Violation


ASSERTIVE_MARKERS = [
    "all tests passed",
    "tests passed",
    "production-ready",
    "production ready",
    "secure",
    "no secrets leaked",
    "no secret leaked",
    "no credentials leaked",
    "verified",
    "confirmed",
    "deployment-ready",
    "deployment ready",
]

FACTUAL_MARKERS = [
    "passed",
    "failed",
    "verified",
    "confirmed",
    "secure",
    "leaked",
    "exists",
    "missing",
    "created",
    "updated",
    "deployed",
    "ran",
]

WEAK_SOURCE_TYPES = {"internal", "unknown"}


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_]+", text.lower()))


def _content_tokens(text: str) -> set[str]:
    stopwords = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "have",
        "if",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "was",
        "were",
        "with",
    }
    return {token for token in _tokens(text) if token not in stopwords and len(token) > 2}


def _claim_appears_grounded_in_response(claim_text: str, response_text: str) -> bool:
    claim_norm = _normalize(claim_text)
    response_norm = _normalize(response_text)

    if claim_norm and claim_norm in response_norm:
        return True

    claim_tokens = _content_tokens(claim_text)
    if not claim_tokens:
        return False

    response_tokens = _content_tokens(response_text)
    overlap = len(claim_tokens & response_tokens) / len(claim_tokens)
    return overlap >= 0.45


def _looks_factual(text: str) -> bool:
    normalized = _normalize(text)
    return any(marker in normalized for marker in FACTUAL_MARKERS)


def check_ledger_integrity(req: VerifyRequest) -> list[Violation]:
    """Check whether claims/evidence are plausible, complete, and auditable."""
    violations: list[Violation] = []
    response_norm = _normalize(req.response_text)
    claim_text_norms = [_normalize(claim.text) for claim in req.claims]

    claims_by_evidence: dict[str, list[str]] = defaultdict(list)
    for claim in req.claims:
        for evidence_id in claim.evidence_ids:
            claims_by_evidence[evidence_id].append(claim.claim_id)

    for claim in req.claims:
        if not _claim_appears_grounded_in_response(claim.text, req.response_text):
            violations.append(
                Violation(
                    rule_id="LEDGER_CLAIM_NOT_IN_RESPONSE",
                    name="Ledger Claim Not In Response",
                    severity=3,
                    claim_id=claim.claim_id,
                    message=(
                        "Claim text is not sufficiently present in the response_text. "
                        "The ledger may be misrepresenting or inventing the response claim."
                    ),
                )
            )

        if claim.type == "speculation" and _looks_factual(claim.text):
            violations.append(
                Violation(
                    rule_id="LEDGER_TYPE_MISCLASSIFICATION",
                    name="Ledger Type Misclassification",
                    severity=3,
                    claim_id=claim.claim_id,
                    message=(
                        "Claim is labeled speculation but contains factual/verification language. "
                        "Do not hide factual claims by lowering their type."
                    ),
                )
            )

    for marker in ASSERTIVE_MARKERS:
        if marker in response_norm and not any(marker in claim_text for claim_text in claim_text_norms):
            violations.append(
                Violation(
                    rule_id="LEDGER_MISSING_CLAIMS",
                    name="Ledger Missing Response Claim",
                    severity=3,
                    message=(
                        f"Response contains assertive claim marker '{marker}' but no ledger claim covers it."
                    ),
                )
            )

    for evidence in req.evidence:
        referenced_by_claim = bool(claims_by_evidence.get(evidence.evidence_id))
        if referenced_by_claim and not evidence.quote:
            violations.append(
                Violation(
                    rule_id="EVIDENCE_WITHOUT_QUOTE",
                    name="Evidence Without Quote",
                    severity=3,
                    message=(
                        f"Evidence {evidence.evidence_id} is used by a claim but has no quote/snippet. "
                        "Evidence must include a concrete auditable excerpt."
                    ),
                )
            )

        if referenced_by_claim and evidence.source_type in WEAK_SOURCE_TYPES:
            violations.append(
                Violation(
                    rule_id="EVIDENCE_SELF_ATTESTED",
                    name="Weak Or Self-Attested Evidence",
                    severity=3,
                    message=(
                        f"Evidence {evidence.evidence_id} uses weak source_type '{evidence.source_type}'. "
                        "Claim-supporting evidence must be primary, secondary, tool, or spec unless explicitly downgraded."
                    ),
                )
            )

        if referenced_by_claim and not evidence.url:
            violations.append(
                Violation(
                    rule_id="SOURCE_NOT_VERIFIABLE",
                    name="Source Not Verifiable",
                    severity=3,
                    message=f"Evidence {evidence.evidence_id} is used by a claim but has no url/source locator.",
                )
            )

    return violations
