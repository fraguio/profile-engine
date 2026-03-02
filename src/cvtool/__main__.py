from __future__ import annotations

import argparse
import json
from pathlib import Path

from cvtool.validate import validate_jsonresume


def main() -> int:
    parser = argparse.ArgumentParser(prog="cvtool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--in", dest="input_path", required=True)

    args = parser.parse_args()

    if args.command == "validate":
        input_path = Path(args.input_path)
        try:
            errors = validate_jsonresume(input_path)
        except json.JSONDecodeError as exc:
            print(f"$: invalid JSON ({exc.msg})")
            return 1
        except FileNotFoundError as exc:
            print(f"$: file not found ({exc.filename})")
            return 1

        if errors:
            for error in errors:
                print(error)
            return 1

        print("OK")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
