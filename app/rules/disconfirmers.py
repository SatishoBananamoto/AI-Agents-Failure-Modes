"""Disconfirmer checks for ICIF-AES verifier v0.2."""

from __future__ import annotations

from collections import defaultdict

from app.fm_taxonomy import FM
from app.schemas import VerifyRequest, Violation


DISCONFIRMER_REQUIRED_TYPES = {"factual", "recommendation"}

VAGUE_DISCONFIRMERS = {
    "maybe something could be wrong",
    "something could be wrong",
    "something might be wrong",
    "maybe wrong",
    "not sure",
    "unknown issue",
}


def _is_specific_enough(text: str) -> bool:
    normalized = " ".join(text.lower().strip().split())
    if normalized in VAGUE_DISCONFIRMERS:
        return False
    if normalized.startswith("maybe "):
        return False
    return len(normalized.split()) >= 6


def check_disconfirmers(req: VerifyRequest) -> list[Violation]:
    """Require testable disconfirmers for high-confidence factual/recommendation claims."""
    violations: list[Violation] = []
    claim_ids = {claim.claim_id for claim in req.claims}
    evidence_ids = {evidence.evidence_id for evidence in req.evidence}

    disconfirmers_by_claim: dict[str, list] = defaultdict(list)

    for disconfirmer in req.disconfirmers:
        disconfirmers_by_claim[disconfirmer.claim_id].append(disconfirmer)

        if disconfirmer.claim_id not in claim_ids:
            violations.append(
                Violation(
                    rule_id="DISCONFIRMER_ORPHAN",
                    name="Disconfirmer References Missing Claim",
                    severity=3,
                    claim_id=disconfirmer.claim_id,
                    message=(
                        f"Disconfirmer {disconfirmer.disconfirmer_id} references missing "
                        f"claim_id: {disconfirmer.claim_id}"
                    ),
                )
            )

        if not _is_specific_enough(disconfirmer.text):
            violations.append(
                Violation(
                    rule_id="DISCONFIRMER_INVALID",
                    name="Invalid Disconfirmer",
                    severity=3,
                    claim_id=disconfirmer.claim_id,
                    message=(
                        f"Disconfirmer {disconfirmer.disconfirmer_id} is too vague; "
                        "it must describe a concrete observation that would weaken or overturn the claim."
                    ),
                )
            )

        for evidence_id in disconfirmer.evidence_ids:
            if evidence_id not in evidence_ids:
                violations.append(
                    Violation(
                        rule_id="DISCONFIRMER_EVIDENCE_MISSING",
                        name="Disconfirmer Evidence Missing",
                        severity=3,
                        claim_id=disconfirmer.claim_id,
                        message=(
                            f"Disconfirmer {disconfirmer.disconfirmer_id} references missing "
                            f"evidence_id: {evidence_id}"
                        ),
                    )
                )

        if disconfirmer.status == "not_checked":
            violations.append(
                Violation(
                    rule_id="DISCONFIRMER_UNCHECKED",
                    name="Disconfirmer Not Checked",
                    severity=3,
                    claim_id=disconfirmer.claim_id,
                    message=(
                        f"Disconfirmer {disconfirmer.disconfirmer_id} exists but was not checked. "
                        "High-impact claims require checked_absent or checked_present."
                    ),
                )
            )

        if disconfirmer.status == "checked_present":
            violations.append(
                Violation(
                    rule_id="DISCONFIRMER_PRESENT",
                    name="Disconfirmer Present",
                    severity=3,
                    claim_id=disconfirmer.claim_id,
                    message=(
                        f"Disconfirmer {disconfirmer.disconfirmer_id} was checked and found present; "
                        "the claim is contradicted or needs revision."
                    ),
                )
            )

    for claim in req.claims:
        requires_disconfirmer = (
            claim.confidence == "high" and claim.type in DISCONFIRMER_REQUIRED_TYPES
        )
        if requires_disconfirmer and not disconfirmers_by_claim.get(claim.claim_id):
            violations.append(
                Violation(
                    rule_id="DISCONFIRMER_REQUIRED",
                    name="Disconfirmer Required",
                    severity=3,
                    claim_id=claim.claim_id,
                    message=(
                        "High-confidence factual/recommendation claim requires at least one "
                        "specific disconfirmer."
                    ),
                )
            )

    return violations
