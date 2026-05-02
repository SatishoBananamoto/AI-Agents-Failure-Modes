"""Confidence-calibration checks for ICIF-AES verifier."""

from app.fm_taxonomy import FM
from app.schemas import VerifyRequest, Violation


def check_confidence(req: VerifyRequest) -> list[Violation]:
    """Catch simple confidence/evidence mismatches."""
    violations: list[Violation] = []

    for claim in req.claims:
        if claim.confidence == "high" and claim.type == "speculation":
            violations.append(
                Violation(
                    rule_id="FM6",
                    name=FM["FM6"],
                    severity=2,
                    claim_id=claim.claim_id,
                    message="Speculative claim cannot carry high confidence.",
                )
            )

        if claim.confidence == "high" and not claim.evidence_ids and claim.type != "speculation":
            violations.append(
                Violation(
                    rule_id="FM6",
                    name=FM["FM6"],
                    severity=3,
                    claim_id=claim.claim_id,
                    message="High-confidence non-speculative claim has no supporting evidence.",
                )
            )

    return violations
