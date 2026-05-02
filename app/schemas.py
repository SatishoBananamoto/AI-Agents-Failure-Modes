"""Pydantic schemas for ICIF-AES verifier v0.2."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


Confidence = Literal["low", "medium", "high"]
ClaimType = Literal["factual", "interpretive", "recommendation", "speculation"]
SourceType = Literal["primary", "secondary", "tool", "spec", "internal", "unknown"]
DisconfirmerStatus = Literal["checked_absent", "checked_present", "not_checked"]
DisconfirmerType = Literal[
    "tool_result",
    "source_conflict",
    "counterexample",
    "assumption_break",
    "temporal_change",
]


class Claim(BaseModel):
    claim_id: str
    text: str
    type: ClaimType
    confidence: Confidence
    evidence_ids: list[str] = Field(default_factory=list)
    time_sensitive: bool = False
    as_of_date: str | None = None


class Evidence(BaseModel):
    evidence_id: str
    source_type: SourceType = "unknown"
    url: str | None = None
    as_of_date: str | None = None
    supports_claim_ids: list[str] = Field(default_factory=list)


class Disconfirmer(BaseModel):
    disconfirmer_id: str
    claim_id: str
    text: str
    check_type: DisconfirmerType
    status: DisconfirmerStatus
    evidence_ids: list[str] = Field(default_factory=list)


class VerifyRequest(BaseModel):
    session_id: str
    as_of_date: str
    response_text: str
    claims: list[Claim] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    disconfirmers: list[Disconfirmer] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Violation(BaseModel):
    rule_id: str
    name: str
    severity: int = Field(ge=1, le=3)
    message: str
    claim_id: str | None = None


class VerifyResponse(BaseModel):
    pass_: bool = Field(alias="pass")
    score: float = Field(ge=0.0, le=1.0)
    severity_max: int = Field(ge=0, le=3)
    violations: list[Violation]
    required_fixes: list[str]

    model_config = {"populate_by_name": True}
