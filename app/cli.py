"""CLI entrypoint for ICIF-AES verifier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from app.schemas import VerifyRequest
from app.verifier import verify


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify an ICIF-AES session JSON file.")
    parser.add_argument("input", help="Path to a verifier request JSON file.")
    args = parser.parse_args(argv)

    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        request = VerifyRequest(**payload)
    except FileNotFoundError:
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 2
    except ValidationError as exc:
        print(f"Invalid verifier request:\n{exc}", file=sys.stderr)
        return 2

    result = verify(request)
    print(result.model_dump_json(by_alias=True, indent=2))
    return 0 if result.pass_ else 1


if __name__ == "__main__":
    raise SystemExit(main())
