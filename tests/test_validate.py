from __future__ import annotations

import json
import subprocess
import sys


def test_validate_accepts_minimal_jsonresume(tmp_path) -> None:
    input_file = tmp_path / "valid.json"
    input_file.write_text(json.dumps({}), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "cvtool", "validate", "--in", str(input_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "OK"


def test_validate_rejects_invalid_jsonresume(tmp_path) -> None:
    input_file = tmp_path / "invalid.json"
    input_file.write_text(json.dumps([]), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "cvtool", "validate", "--in", str(input_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 3
    assert "Error:" in result.stderr
