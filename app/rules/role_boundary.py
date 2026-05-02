"""Role-boundary checks for ICIF-AES verifier."""

from app.fm_taxonomy import FM
from app.schemas import VerifyRequest, Violation


ADVOCACY_PHRASES = [
    "this proves",
    "undeniably",
    "clearly superior",
    "no need to consider",
    "obviously correct",
]


def check_role_boundary(req: VerifyRequest) -> list[Violation]:
    """Flag simple verifier-role collapse into advocacy language."""
    role = str(req.metadata.get("model_role", "")).lower()
    text_lower = req.response_text.lower()
    violations: list[Violation] = []

    if role == "verifier":
        for phrase in ADVOCACY_PHRASES:
            if phrase in text_lower:
                violations.append(
                    Violation(
                        rule_id="FM5",
                        name=FM["FM5"],
                        severity=2,
                        message=f"Verifier response appears advocacy-like: '{phrase}'",
                    )
                )

    return violations
