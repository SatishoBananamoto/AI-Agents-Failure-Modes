"""Deterministic ICIF-AES verifier engine."""

from app.rules.confidence import check_confidence
from app.rules.contamination import check_independent_derivation
from app.rules.evidence import check_evidence
from app.rules.protocol import check_protocol
from app.rules.role_boundary import check_role_boundary
from app.rules.temporal import check_temporal_grounding
from app.schemas import VerifyRequest, VerifyResponse, Violation


RULES = [
    check_protocol,
    check_evidence,
    check_temporal_grounding,
    check_confidence,
    check_role_boundary,
    check_independent_derivation,
]


def verify(req: VerifyRequest) -> VerifyResponse:
    """Run all deterministic rules and produce a CI-friendly verdict."""
    violations: list[Violation] = []

    for rule in RULES:
        violations.extend(rule(req))

    severity_max = max((violation.severity for violation in violations), default=0)
    penalty = sum(violation.severity for violation in violations)
    score = max(0.0, 1.0 - penalty / 20.0)

    # v0.1 is a hard-gate verifier: any violation fails the run.
    # Severity and score still help rank fixes, but PASS means clean.
    passed = len(violations) == 0

    required_fixes = [
        f"{violation.claim_id}: {violation.message}" if violation.claim_id else violation.message
        for violation in violations
    ]

    return VerifyResponse(
        pass_=passed,
        score=round(score, 3),
        severity_max=severity_max,
        violations=violations,
        required_fixes=required_fixes,
    )
