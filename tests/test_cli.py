from __future__ import annotations

import subprocess
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


def test_render_html_missing_input_returns_io_error() -> None:
    result = runner.invoke(app, ["render-html", "missing.yaml"])
    assert result.exit_code == 4
    assert "I/O error" in result.output


def test_render_html_rejects_stdout_output_path() -> None:
    yaml_path = Path(__file__).resolve().parents[1] / "examples" / "rendercv.example.yaml"
    result = runner.invoke(app, ["render-html", str(yaml_path), "--output", "-"])
    assert result.exit_code == 2


def test_render_html_runs_rendercv(monkeypatch, tmp_path) -> None:
    input_yaml = tmp_path / "rendercv.yaml"
    input_yaml.write_text("cv:\n  name: Jane Doe\n", encoding="utf-8")
    output_html = tmp_path / "site" / "index.html"

    called: dict[str, object] = {}

    def fake_run(command: list[str], capture_output: bool, text: bool, check: bool) -> subprocess.CompletedProcess[str]:
        called["command"] = command
        called["capture_output"] = capture_output
        called["text"] = text
        called["check"] = check
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", fake_run)

    result = runner.invoke(app, ["render-html", str(input_yaml), "--output", str(output_html)])

    assert result.exit_code == 0
    command = called["command"]
    assert isinstance(command, list)
    assert command[:2] == ["rendercv", "render"]
    assert "--html-path" in command
    assert str(output_html.resolve()) in command


def test_html_runs_validate_convert_and_render(monkeypatch, tmp_path) -> None:
    resume_path = Path(__file__).resolve().parents[1] / "examples" / "resume.example.json"
    yaml_output = tmp_path / "output" / "rendercv_CV.yaml"
    html_output = tmp_path / "output" / "index.html"

    captured: dict[str, str] = {}

    def fake_render(input_yaml_path: str, html_output_path: str) -> None:
        captured["input_yaml_path"] = input_yaml_path
        captured["html_output_path"] = html_output_path

    monkeypatch.setattr("profilecli.cli._run_render_html", fake_render)

    result = runner.invoke(
        app,
        [
            "html",
            "--in",
            str(resume_path),
            "--output",
            str(yaml_output),
            "--html-output",
            str(html_output),
        ],
    )

    assert result.exit_code == 0
    assert yaml_output.exists()
    assert captured["input_yaml_path"] == str(yaml_output)
    assert captured["html_output_path"] == str(html_output)
