"""Deterministic verifier for raw agent session logs."""

from app.rules.session_consistency import check_session_consistency
from app.schemas import Violation
from app.session_schemas import SessionVerifyRequest, SessionVerifyResponse


RULES = [
    check_session_consistency,
]


def verify_session(req: SessionVerifyRequest) -> SessionVerifyResponse:
    """Run raw-session consistency checks and produce a CI-friendly verdict."""
    violations: list[Violation] = []

    for rule in RULES:
        violations.extend(rule(req))

    severity_max = max((violation.severity for violation in violations), default=0)
    penalty = sum(violation.severity for violation in violations)
    score = max(0.0, 1.0 - penalty / 20.0)
    passed = len(violations) == 0

    return SessionVerifyResponse(
        pass_=passed,
        score=round(score, 3),
        severity_max=severity_max,
        violations=violations,
        required_fixes=[violation.message for violation in violations],
    )
