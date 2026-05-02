import json
from pathlib import Path

from app.schemas import VerifyRequest
from app.verifier import verify


FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> VerifyRequest:
    raw = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return VerifyRequest(**raw)


def test_pass_basic():
    result = verify(load_fixture("pass_basic.json"))
    assert result.pass_ is True
    assert result.severity_max == 0
    assert result.violations == []


def test_fail_missing_header():
    result = verify(load_fixture("fail_no_header.json"))
    assert result.pass_ is False
    assert any(v.rule_id == "PROTO_HEADER" for v in result.violations)


def test_fail_ungrounded_claim():
    result = verify(load_fixture("fail_ungrounded_claim.json"))
    assert result.pass_ is False
    assert any(v.rule_id == "FM1" for v in result.violations)


def test_fail_temporal_claim_without_date():
    result = verify(load_fixture("fail_temporal.json"))
    assert result.pass_ is False
    assert any(v.rule_id == "FM4" for v in result.violations)


def test_fail_high_confidence_without_evidence():
    result = verify(load_fixture("fail_confidence.json"))
    assert result.pass_ is False
    assert any(v.rule_id == "FM6" for v in result.violations)


def test_fail_independent_derivation_required():
    result = verify(load_fixture("fail_independent_derivation.json"))
    assert result.pass_ is False
    assert any(v.rule_id == "FM13" for v in result.violations)


def test_fail_missing_disconfirmer():
    result = verify(load_fixture("fail_disconfirmer_missing.json"))
    assert result.pass_ is False
    assert any(v.rule_id == "DISCONFIRMER_REQUIRED" for v in result.violations)


def test_fail_unchecked_disconfirmer():
    result = verify(load_fixture("fail_disconfirmer_unchecked.json"))
    assert result.pass_ is False
    assert any(v.rule_id == "DISCONFIRMER_UNCHECKED" for v in result.violations)
