"""Schemas for verifying raw agent session logs."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas import Violation


SessionRole = Literal["system", "user", "assistant", "tool"]
SessionEventType = Literal["message", "tool_result"]


class SessionEvent(BaseModel):
    role: SessionRole
    content: str
    name: str | None = None
    event_type: SessionEventType = "message"
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionVerifyRequest(BaseModel):
    session_id: str
    as_of_date: str
    messages: list[SessionEvent] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionVerifyResponse(BaseModel):
    pass_: bool = Field(alias="pass")
    score: float = Field(ge=0.0, le=1.0)
    severity_max: int = Field(ge=0, le=3)
    violations: list[Violation]
    required_fixes: list[str]

    model_config = {"populate_by_name": True}
