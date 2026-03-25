from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from profilecli.cli import app


runner = CliRunner()


def test_help_returns_zero() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_export_file_to_stdout_returns_yaml() -> None:
    resume_path = Path(__file__).resolve().parents[1] / "resume.example.json"
    result = runner.invoke(app, ["export", str(resume_path), "-o", "-"])
    assert result.exit_code == 0
    assert result.stdout.strip() != ""


def test_export_from_stdin_to_stdout() -> None:
    resume_path = Path(__file__).resolve().parents[1] / "resume.example.json"
    payload = resume_path.read_text(encoding="utf-8")
    result = runner.invoke(app, ["export", "-i", "-", "-o", "-"], input=payload)
    assert result.exit_code == 0
    assert result.stdout.strip() != ""


def test_export_missing_file_returns_io_error() -> None:
    result = runner.invoke(app, ["export", "missing.json", "-o", "-"])
    assert result.exit_code == 4
    assert "I/O error" in result.output


def test_export_invalid_format_returns_usage_error() -> None:
    resume_path = Path(__file__).resolve().parents[1] / "resume.example.json"
    result = runner.invoke(app, ["export", str(resume_path), "--format", "foo", "-o", "-"])
    assert result.exit_code == 2


def test_export_invalid_json_from_stdin_returns_parse_error() -> None:
    result = runner.invoke(app, ["export", "-i", "-"], input="{not-json")
    assert result.exit_code == 3


def test_export_json_root_must_be_object() -> None:
    result = runner.invoke(app, ["export", "-i", "-", "-o", "-"], input="[]")
    assert result.exit_code == 3
    assert "Error: JSON root must be an object" in result.output
