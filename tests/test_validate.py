from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_validate_accepts_resume_example() -> None:
    input_file = Path(__file__).resolve().parents[1] / "resume.example.json"

    result = subprocess.run(
        [sys.executable, "-m", "cvtool", "validate", "--in", str(input_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "OK"


def test_validate_rejects_invalid_json(tmp_path) -> None:
    input_file = tmp_path / "broken.json"
    input_file.write_text("{broken", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "cvtool", "validate", "--in", str(input_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 3
    assert "Error:" in result.stderr


def test_validate_missing_file_returns_io_error(tmp_path) -> None:
    input_file = tmp_path / "missing.json"

    result = subprocess.run(
        [sys.executable, "-m", "cvtool", "validate", "--in", str(input_file)],
        capture_output=True,
        text=True,
        check=False,
    )

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

    result = subprocess.run(
        [sys.executable, "-m", "cvtool", "validate", "--in", str(input_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 3
    assert "Error:" in result.stderr
    assert "startDate" in result.stderr
