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

    rendercv_parser = subparsers.add_parser("rendercv")
    rendercv_parser.add_argument("input_path")
    rendercv_parser.add_argument("-o", "--out", dest="output_path")

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

    if args.command == "rendercv":
        from cvtool.convert_rendercv import convert_file
        input_path = Path(args.input_path)
        output_path = Path(args.output_path) if args.output_path else None
        try:
            yaml_output = convert_file(input_path, output_path)
        except json.JSONDecodeError as exc:
            print(f"$: invalid JSON ({exc.msg})")
            return 1
        except FileNotFoundError as exc:
            print(f"$: file not found ({exc.filename})")
            return 1

        if yaml_output is not None:
            print(yaml_output, end="")

        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
