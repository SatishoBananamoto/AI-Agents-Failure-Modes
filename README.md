# ICIF-AES Verifier

A deterministic verifier for ICIF-AES response packets, claim ledgers, evidence ledgers, disconfirmers, and failure-mode gates.

This repository starts with a deliberately small v0.2 scope: hard protocol and epistemic checks before any LLM-judge layer.

## What v0.2 checks

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
- High-confidence factual/recommendation claims require a specific disconfirmer
- Unchecked disconfirmers fail the run
- Present disconfirmers fail the claim until revised
- Vague, orphaned, or evidence-broken disconfirmers fail the run

## Disconfirmer model

Evidence asks: `Why might this be true?`

A disconfirmer asks: `What concrete observation would weaken or overturn this?`

Example:

```json
{
  "disconfirmer_id": "D1",
  "claim_id": "C1",
  "text": "A later relevant test run fails after the claimed passing run.",
  "check_type": "tool_result",
  "status": "checked_absent",
  "evidence_ids": ["E2"]
}
```

Allowed statuses:

- `checked_absent`: the disconfirming condition was checked and not found
- `checked_present`: the disconfirming condition was found, so the claim fails
- `not_checked`: the disconfirming condition exists but was not checked, so the run fails

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
