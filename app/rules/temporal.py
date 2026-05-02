"""Temporal-grounding checks for ICIF-AES verifier."""

from app.fm_taxonomy import FM
from app.schemas import VerifyRequest, Violation


def check_temporal_grounding(req: VerifyRequest) -> list[Violation]:
    """Ensure time-sensitive claims are explicitly dated."""
    violations: list[Violation] = []

    for claim in req.claims:
        if claim.time_sensitive and not claim.as_of_date:
            violations.append(
                Violation(
                    rule_id="FM4",
                    name=FM["FM4"],
                    severity=2,
                    claim_id=claim.claim_id,
                    message="Time-sensitive claim lacks claim-level as_of_date.",
                )
            )

    return violations
