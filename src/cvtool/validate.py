from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator


def _format_json_path(path_parts: list[object]) -> str:
    path = "$"
    for part in path_parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def validate_jsonresume(input_path: Path) -> list[str]:
    project_root = Path(__file__).resolve().parents[2]
    schema_path = project_root / "schemas" / "jsonresume.schema.json"

    with schema_path.open("r", encoding="utf-8") as schema_file:
        schema = json.load(schema_file)

    with input_path.open("r", encoding="utf-8") as input_file:
        payload = json.load(input_file)

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    return [f"{_format_json_path(list(err.path))}: {err.message}" for err in errors]
