"""Evidence-ledger checks for ICIF-AES verifier."""

from app.fm_taxonomy import FM
from app.schemas import VerifyRequest, Violation


def check_evidence(req: VerifyRequest) -> list[Violation]:
    """Ensure factual claims have evidence and references resolve."""
    evidence_by_id = {item.evidence_id: item for item in req.evidence}
    violations: list[Violation] = []

    for claim in req.claims:
        if claim.type == "factual" and not claim.evidence_ids:
            violations.append(
                Violation(
                    rule_id="FM1",
                    name=FM["FM1"],
                    severity=3,
                    claim_id=claim.claim_id,
                    message="Factual claim has no evidence_ids.",
                )
            )

        for evidence_id in claim.evidence_ids:
            evidence = evidence_by_id.get(evidence_id)
            if evidence is None:
                violations.append(
                    Violation(
                        rule_id="FM1",
                        name=FM["FM1"],
                        severity=3,
                        claim_id=claim.claim_id,
                        message=f"Claim references missing evidence_id: {evidence_id}",
                    )
                )
                continue

            if evidence.supports_claim_ids and claim.claim_id not in evidence.supports_claim_ids:
                violations.append(
                    Violation(
                        rule_id="FM1",
                        name=FM["FM1"],
                        severity=2,
                        claim_id=claim.claim_id,
                        message=f"Evidence {evidence_id} does not list claim {claim.claim_id} in supports_claim_ids.",
                    )
                )

    return violations
