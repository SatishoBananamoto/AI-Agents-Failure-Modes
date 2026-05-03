"""Session-level consistency checks for raw agent logs."""

from __future__ import annotations

from app.schemas import Violation
from app.session_schemas import SessionEvent, SessionVerifyRequest


SUCCESS_MARKERS = [
    "tests passed",
    "all tests passed",
    "build passed",
    "all checks passed",
    "no failures",
    "done",
    "completed",
]

TEST_CLAIM_MARKERS = ["tests passed", "all tests passed", "pytest passed", "test suite passed"]
BUILD_CLAIM_MARKERS = ["build passed", "docker build passed", "image built", "build succeeded"]
SECURITY_CLAIM_MARKERS = ["secure", "no secrets leaked", "no credentials leaked", "no leaks"]

FAILURE_MARKERS = ["failed", "failures", "error", "errors", "traceback", "exit code 1"]
PASS_MARKERS = ["passed", "success", "exit code 0", "0 failed"]
TEST_TOOL_NAMES = {"pytest", "test", "tests", "npm test", "unit-tests"}
BUILD_TOOL_NAMES = {"docker", "docker build", "build", "npm build"}
SECURITY_TOOL_NAMES = {"secret-scan", "security-scan", "gitleaks", "trufflehog", "bandit"}


def _norm(text: str | None) -> str:
    return " ".join((text or "").lower().strip().split())


def _contains_any(text: str, markers: list[str]) -> bool:
    return any(marker in text for marker in markers)


def _is_tool_event(event: SessionEvent) -> bool:
    return event.role == "tool" or event.event_type == "tool_result"


def _tool_name(event: SessionEvent) -> str:
    return _norm(event.name or event.metadata.get("command") or event.metadata.get("tool") or "")


def _tool_category(event: SessionEvent) -> str | None:
    name = _tool_name(event)
    content = _norm(event.content)

    if any(tool in name for tool in TEST_TOOL_NAMES) or "pytest" in content or "tests/" in content:
        return "test"
    if any(tool in name for tool in BUILD_TOOL_NAMES) or "docker build" in content:
        return "build"
    if any(tool in name for tool in SECURITY_TOOL_NAMES) or "secret" in content or "credential" in content:
        return "security"
    return None


def _tool_status(event: SessionEvent) -> str | None:
    content = _norm(event.content)
    metadata_status = _norm(str(event.metadata.get("status", "")))
    exit_code = event.metadata.get("exit_code")

    if exit_code not in (None, ""):
        return "pass" if str(exit_code) == "0" else "fail"

    if metadata_status in {"pass", "passed", "success", "succeeded", "ok"}:
        return "pass"
    if metadata_status in {"fail", "failed", "failure", "error"}:
        return "fail"

    if _contains_any(content, FAILURE_MARKERS):
        return "fail"
    if _contains_any(content, PASS_MARKERS):
        return "pass"
    return None


def _latest_tool_result(req: SessionVerifyRequest, category: str) -> SessionEvent | None:
    for event in reversed(req.messages):
        if _is_tool_event(event) and _tool_category(event) == category:
            return event
    return None


def _has_tool_result(req: SessionVerifyRequest, category: str) -> bool:
    return any(_is_tool_event(event) and _tool_category(event) == category for event in req.messages)


def _assistant_final(req: SessionVerifyRequest) -> SessionEvent | None:
    for event in reversed(req.messages):
        if event.role == "assistant":
            return event
    return None


def check_session_consistency(req: SessionVerifyRequest) -> list[Violation]:
    """Compare final assistant claims against relevant tool events."""
    violations: list[Violation] = []
    final = _assistant_final(req)
    if final is None:
        return [
            Violation(
                rule_id="SESSION_NO_ASSISTANT_FINAL",
                name="Missing Assistant Final Message",
                severity=3,
                message="Session has no assistant message to verify.",
            )
        ]

    final_text = _norm(final.content)

    claims_tests_passed = _contains_any(final_text, TEST_CLAIM_MARKERS)
    claims_build_passed = _contains_any(final_text, BUILD_CLAIM_MARKERS)
    claims_security_ok = _contains_any(final_text, SECURITY_CLAIM_MARKERS)

    if claims_tests_passed:
        latest_test = _latest_tool_result(req, "test")
        if latest_test is None:
            violations.append(
                Violation(
                    rule_id="MISSING_TOOL_EVIDENCE",
                    name="Missing Tool Evidence",
                    severity=3,
                    message="Assistant claims tests passed, but no test tool result exists in the session.",
                )
            )
        elif _tool_status(latest_test) == "fail":
            violations.append(
                Violation(
                    rule_id="FINAL_CLAIM_CONTRADICTS_TOOL_RESULT",
                    name="Final Claim Contradicts Tool Result",
                    severity=3,
                    message="Assistant claims tests passed, but the latest relevant test tool result failed.",
                )
            )

    if claims_build_passed:
        latest_build = _latest_tool_result(req, "build")
        if latest_build is None:
            violations.append(
                Violation(
                    rule_id="MISSING_TOOL_EVIDENCE",
                    name="Missing Tool Evidence",
                    severity=3,
                    message="Assistant claims build succeeded, but no build tool result exists in the session.",
                )
            )
        elif _tool_status(latest_build) == "fail":
            violations.append(
                Violation(
                    rule_id="FINAL_CLAIM_CONTRADICTS_TOOL_RESULT",
                    name="Final Claim Contradicts Tool Result",
                    severity=3,
                    message="Assistant claims build succeeded, but the latest relevant build result failed.",
                )
            )

    if claims_security_ok and not _has_tool_result(req, "security"):
        violations.append(
            Violation(
                rule_id="UNVERIFIED_SECURITY_CLAIM",
                name="Unverified Security Claim",
                severity=3,
                message="Assistant makes a security/no-leak claim without a matching security scan/tool result.",
            )
        )

    # Stale success: any assistant success claim after an earlier pass must be invalidated
    # by a later relevant failure before the final answer.
    if claims_tests_passed:
        seen_pass = False
        stale_failure_after_pass = False
        for event in req.messages:
            if _is_tool_event(event) and _tool_category(event) == "test":
                status = _tool_status(event)
                if status == "pass":
                    seen_pass = True
                elif status == "fail" and seen_pass:
                    stale_failure_after_pass = True
        if stale_failure_after_pass:
            violations.append(
                Violation(
                    rule_id="STALE_SUCCESS_CLAIM",
                    name="Stale Success Claim",
                    severity=3,
                    message="Assistant claims tests passed, but a later relevant test run failed after an earlier pass.",
                )
            )

    if _contains_any(final_text, SUCCESS_MARKERS) and not (
        claims_tests_passed or claims_build_passed or claims_security_ok
    ):
        # Generic done/completed claims are allowed. This placeholder keeps the rule explicit.
        pass

    return violations
