"""Protocol-level checks for ICIF-AES response packets."""

from app.schemas import VerifyRequest, Violation


REQUIRED_HEADER_FIELDS = [
    "To:",
    "From:",
    "Session ID:",
    "Conversational State:",
    "Anchor Points:",
]


def check_protocol(req: VerifyRequest) -> list[Violation]:
    """Check required ICIF-AES packet wrapper and footer fields."""
    text = req.response_text
    violations: list[Violation] = []

    if "[ICIF-AES Response Packet]" not in text:
        violations.append(
            Violation(
                rule_id="PROTO_HEADER",
                name="Missing ICIF-AES Header",
                severity=3,
                message="Response does not include required ICIF-AES response packet header.",
            )
        )

    for field in REQUIRED_HEADER_FIELDS:
        if field not in text:
            violations.append(
                Violation(
                    rule_id="PROTO_HEADER_FIELD",
                    name="Missing Header Field",
                    severity=2,
                    message=f"Missing required header field: {field}",
                )
            )

    if "Δ-info" not in text and "Delta-info" not in text:
        violations.append(
            Violation(
                rule_id="PROTO_DELTA",
                name="Missing Delta-info Footer",
                severity=3,
                message="Response does not include required Δ-info footer.",
            )
        )

    return violations
