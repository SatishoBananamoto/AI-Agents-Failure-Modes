import json

from app.cli import main as cli_main
from app.session_schemas import SessionVerifyRequest
from app.session_verifier import verify_session


def make_session(messages: list[dict]) -> SessionVerifyRequest:
    return SessionVerifyRequest(
        session_id="ICIF-AES-SESSION-TEST",
        as_of_date="2026-05-12",
        messages=messages,
    )


def test_session_passes_when_final_test_claim_matches_tool_pass():
    req = make_session(
        [
            {
                "role": "tool",
                "event_type": "tool_result",
                "name": "pytest",
                "content": "32 passed",
                "metadata": {"exit_code": 0},
            },
            {"role": "assistant", "content": "Tests passed."},
        ]
    )

    result = verify_session(req)

    assert result.pass_ is True
    assert result.violations == []


def test_session_fails_when_final_test_claim_contradicts_latest_tool_result():
    req = make_session(
        [
            {
                "role": "tool",
                "event_type": "tool_result",
                "name": "pytest",
                "content": "32 passed",
                "metadata": {"exit_code": 0},
            },
            {
                "role": "tool",
                "event_type": "tool_result",
                "name": "pytest",
                "content": "1 failed",
                "metadata": {"exit_code": 1},
            },
            {"role": "assistant", "content": "Tests passed."},
        ]
    )

    result = verify_session(req)

    assert result.pass_ is False
    assert {violation.rule_id for violation in result.violations} == {
        "FINAL_CLAIM_CONTRADICTS_TOOL_RESULT",
        "STALE_SUCCESS_CLAIM",
    }


def test_session_fails_security_claim_without_security_tool_result():
    req = make_session(
        [
            {"role": "assistant", "content": "No secrets leaked."},
        ]
    )

    result = verify_session(req)

    assert result.pass_ is False
    assert any(violation.rule_id == "UNVERIFIED_SECURITY_CLAIM" for violation in result.violations)


def test_cli_auto_detects_raw_session_payload(tmp_path, capsys):
    payload = {
        "session_id": "ICIF-AES-SESSION-CLI-001",
        "as_of_date": "2026-05-12",
        "messages": [
            {
                "role": "tool",
                "event_type": "tool_result",
                "name": "pytest",
                "content": "32 passed",
                "metadata": {"exit_code": 0},
            },
            {"role": "assistant", "content": "Tests passed."},
        ],
    }
    path = tmp_path / "session.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    assert cli_main([str(path)]) == 0
    captured = capsys.readouterr()
    assert '"pass": true' in captured.out
