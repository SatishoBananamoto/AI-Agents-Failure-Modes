# ICIF-AES Verifier

A deterministic verifier for ICIF-AES response packets, claim ledgers, evidence ledgers, and failure-mode gates.

This repository starts with a deliberately small v0.1 scope: hard protocol and epistemic checks before any LLM-judge layer.

## What v0.1 checks

- Required `[ICIF-AES Response Packet]` header
- Required header fields: `To`, `From`, `Session ID`, `Conversational State`, `Anchor Points`
- Required `Δ-info` footer
- Factual claims mapped to evidence IDs
- Evidence IDs exist in the evidence ledger
- Time-sensitive claims include an `as_of_date`
- High-confidence claims have support
- Speculation cannot be marked high confidence
- Verifier role avoids advocacy language
- Independent derivation marker is present when required

## API

```bash
uvicorn app.main:app --reload
```

```bash
curl -X POST http://127.0.0.1:8000/verify \
  -H 'content-type: application/json' \
  --data @tests/fixtures/pass_basic.json
```

## CLI

```bash
python -m app.cli tests/fixtures/pass_basic.json
```

The CLI exits `0` on PASS and `1` on FAIL, so it can be used in CI or agent hooks.

## Tests

```bash
pytest -q
```

## Design principle

AI systems may write, argue, code, or recommend — but their claims must survive machine-checkable epistemic gates.
