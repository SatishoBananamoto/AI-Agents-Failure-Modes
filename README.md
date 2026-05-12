# ICIF-AES Verifier

A deterministic verifier for ICIF-AES response packets, claim ledgers, evidence ledgers, disconfirmers, ledger integrity, and failure-mode gates.

This repository starts with a deliberately small v0.3 scope: hard protocol and epistemic checks before any LLM-judge layer.

## What v0.3 checks

- Required `[ICIF-AES Response Packet]` header
- Required header fields: `To`, `From`, `Session ID`, `Conversational State`, `Anchor Points`
- Required `Δ-info` footer
- Factual claims mapped to evidence IDs
- Evidence IDs exist in the evidence ledger
- Claim-supporting evidence includes a concrete `quote` / snippet
- Claim-supporting evidence has a source locator (`url`)
- Weak/self-attested evidence types fail when used as claim support
- Time-sensitive claims include an `as_of_date`
- High-confidence claims have support
- Speculation cannot be marked high confidence
- Factual/verification language cannot be hidden as `speculation`
- Verifier role avoids advocacy language
- Independent derivation marker is present when required
- High-confidence factual/recommendation claims require a specific disconfirmer
- Unchecked disconfirmers fail the run
- Present disconfirmers fail the claim until revised
- Vague, orphaned, or evidence-broken disconfirmers fail the run
- Response-level assertive claims such as `tests passed`, `secure`, `verified`, or `no secrets leaked` must appear in the claim ledger
- Ledger claims must be sufficiently grounded in `response_text`
- Raw-session final claims such as `tests passed` or `build passed` must match the latest relevant tool result
- Raw-session security claims such as `no secrets leaked` require a matching security scan/tool result

## Ledger integrity model

The verifier treats the JSON ledger as untrusted input.

The LLM may propose claims, evidence, and disconfirmers, but the verifier checks whether the ledger is structurally consistent with the raw response and auditable evidence snippets.

Example evidence object:

```json
{
  "evidence_id": "E1",
  "source_type": "tool",
  "url": "internal://test-run",
  "quote": "All relevant tests passed.",
  "as_of_date": "2026-05-02",
  "supports_claim_ids": ["C1"]
}
```

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

Raw session consistency checks are also available:

```bash
curl -X POST http://127.0.0.1:8000/verify-session \
  -H 'content-type: application/json' \
  --data @session.json
```

## CLI

```bash
python -m app.cli tests/fixtures/pass_basic.json
```

The CLI also auto-detects raw session payloads with a `messages` list:

```bash
python -m app.cli session.json
```

The CLI exits `0` on PASS and `1` on FAIL, so it can be used in CI or agent hooks.

## Tests

```bash
pytest -q
```

## Design principle

AI systems may write, argue, code, or recommend — but their claims must survive machine-checkable epistemic gates.
