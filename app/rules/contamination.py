"""Cross-contamination and independent-derivation checks."""

from app.fm_taxonomy import FM
from app.schemas import VerifyRequest, Violation


INDEPENDENT_DERIVATION_MARKERS = [
    "independent derivation",
    "independent reframe",
    "alternative frame",
]


def check_independent_derivation(req: VerifyRequest) -> list[Violation]:
    """Require an explicit derivation marker when the session metadata demands it."""
    required = bool(req.metadata.get("requires_independent_derivation", False))
    text_lower = req.response_text.lower()

    has_marker = any(marker in text_lower for marker in INDEPENDENT_DERIVATION_MARKERS)

    if required and not has_marker:
        return [
            Violation(
                rule_id="FM13",
                name=FM["FM13"],
                severity=3,
                message="Independent derivation required but marker/reframe is missing.",
            )
        ]

    return []
