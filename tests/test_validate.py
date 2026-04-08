from __future__ import annotations

import json
from pathlib import Path

from tests.subprocess_cli import run_profilecli_subprocess


def test_validate_accepts_resume_example() -> None:
    input_file = Path(__file__).resolve().parents[1] / "examples" / "resume.example.json"

    result = run_profilecli_subprocess(["validate", "--input", str(input_file)])

    assert result.returncode == 0
    assert result.stdout.strip() == "OK"


def test_validate_accepts_resume_example_as_path_argument() -> None:
    input_file = Path(__file__).resolve().parents[1] / "examples" / "resume.example.json"

    result = run_profilecli_subprocess(["validate", str(input_file)])

    assert result.returncode == 0
    assert result.stdout.strip() == "OK"


def test_validate_rejects_invalid_json(tmp_path) -> None:
    input_file = tmp_path / "broken.json"
    input_file.write_text("{broken", encoding="utf-8")

    result = run_profilecli_subprocess(["validate", "--input", str(input_file)])

    assert result.returncode == 3
    assert "Error:" in result.stderr


def test_validate_missing_file_returns_io_error(tmp_path) -> None:
    input_file = tmp_path / "missing.json"

    result = run_profilecli_subprocess(["validate", "--input", str(input_file)])

    assert result.returncode == 4
    assert "Error:" in result.stderr


def test_validate_rejects_schema_violation_with_field_path(tmp_path) -> None:
    input_file = tmp_path / "invalid-schema.json"
    input_file.write_text(
        json.dumps(
            {
                "work": [
                    {
                        "name": "Acme",
                        "position": "Engineer",
                        "startDate": 202013,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_profilecli_subprocess(["validate", "--input", str(input_file)])

    assert result.returncode == 3
    assert "Error:" in result.stderr
    assert "startDate" in result.stderr
