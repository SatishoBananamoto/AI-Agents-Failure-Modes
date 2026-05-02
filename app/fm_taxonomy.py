"""Canonical ICIF-AES failure mode taxonomy for verifier v0.1."""

FM = {
    "FM1": "Ungrounded Claim",
    "FM2": "Premature Convergence",
    "FM3": "Source Contamination",
    "FM4": "Temporal Grounding Failure",
    "FM5": "Role Boundary Violation",
    "FM6": "Confidence Miscalibration",
    "FM7": "Cherry-Picking",
    "FM8": "Circular Reasoning",
    "FM9": "Missing Operationalization",
    "FM10": "Scope Creep",
    "FM11": "Hidden Assumptions",
    "FM12": "Expertise Boundary Violation",
    "FM13": "Cross-Contamination",
}

PROTOCOL = {
    "PROTO_HEADER": "Missing ICIF-AES Header",
    "PROTO_HEADER_FIELD": "Missing Header Field",
    "PROTO_DELTA": "Missing Delta-info Footer",
}
