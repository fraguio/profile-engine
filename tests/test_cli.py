from __future__ import annotations

from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from profilecli.cli import ExitCode, _resolve_input_source, app


runner = CliRunner()


def test_help_returns_zero() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_convert_file_to_stdout_returns_yaml() -> None:
    resume_path = Path(__file__).resolve().parents[1] / "examples" / "resume.example.json"
    result = runner.invoke(app, ["convert", str(resume_path), "-o", "-"])
    assert result.exit_code == 0
    assert result.stdout.strip() != ""


def test_convert_default_output_is_stdout() -> None:
    resume_path = Path(__file__).resolve().parents[1] / "examples" / "resume.example.json"
    result = runner.invoke(app, ["convert", str(resume_path)])
    assert result.exit_code == 0
    assert result.stdout.strip() != ""


def test_convert_accepts_legacy_resume_example_path() -> None:
    result = runner.invoke(app, ["convert", "resume.example.json"])
    assert result.exit_code == 0
    assert result.stdout.strip() != ""


def test_convert_from_stdin_to_stdout() -> None:
    resume_path = Path(__file__).resolve().parents[1] / "examples" / "resume.example.json"
    payload = resume_path.read_text(encoding="utf-8")
    result = runner.invoke(app, ["convert", "-i", "-", "-o", "-"], input=payload)
    assert result.exit_code == 0
    assert result.stdout.strip() != ""


def test_convert_without_args_reads_from_piped_stdin() -> None:
    resume_path = Path(__file__).resolve().parents[1] / "examples" / "resume.example.json"
    payload = resume_path.read_text(encoding="utf-8")
    result = runner.invoke(app, ["convert"], input=payload)
    assert result.exit_code == 0
    assert result.stdout.strip() != ""


def test_resolve_input_source_without_args_in_tty_returns_usage_error(monkeypatch) -> None:
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    with pytest.raises(typer.Exit) as excinfo:
        _resolve_input_source(None, None)
    assert excinfo.value.exit_code == ExitCode.USAGE


def test_convert_missing_file_returns_io_error() -> None:
    result = runner.invoke(app, ["convert", "missing.json", "-o", "-"])
    assert result.exit_code == 4
    assert "I/O error" in result.output


def test_convert_invalid_format_returns_usage_error() -> None:
    resume_path = Path(__file__).resolve().parents[1] / "examples" / "resume.example.json"
    result = runner.invoke(app, ["convert", str(resume_path), "--format", "foo", "-o", "-"])
    assert result.exit_code == 2


def test_convert_invalid_json_from_stdin_returns_parse_error() -> None:
    result = runner.invoke(app, ["convert", "-i", "-"], input="{not-json")
    assert result.exit_code == 3


def test_convert_json_root_must_be_object() -> None:
    result = runner.invoke(app, ["convert", "-i", "-", "-o", "-"], input="[]")
    assert result.exit_code == 3
    assert "Error: JSON root must be an object" in result.output
