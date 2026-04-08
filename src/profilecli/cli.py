from __future__ import annotations

import json
import subprocess
import sys
from enum import IntEnum
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Annotated

import typer

from profilecli.convert_rendercv import convert_jsonresume_to_rendercv, dump_rendercv_yaml
from profilecli.validate import validate_jsonresume


class ExitCode(IntEnum):
    USAGE = 2
    JSON_PARSE = 3
    IO = 4
    UNEXPECTED = 5


app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help=(
        "Validate and transform JSON Resume data.\n\n"
        "Core flow:\n"
        "validate -> convert -> render-html\n"
        "or use html for the full pipeline."
    ),
)


def _print_version(value: bool) -> None:
    if not value:
        return
    try:
        resolved_version = version("profilectl")
    except PackageNotFoundError:
        resolved_version = "0.0.0"
    typer.echo(resolved_version)
    raise typer.Exit()


@app.callback()
def main(
    version_flag: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_print_version,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = False,
) -> None:
    _ = version_flag


def _resolve_input_source(
    input_arg: Path | None,
    input_option: str | None,
    *,
    allow_stdin: bool,
) -> str:
    if input_arg is not None and input_option is not None:
        typer.echo("Error: pass either input argument or --input, not both.", err=True)
        raise typer.Exit(code=ExitCode.USAGE)
    if input_arg is not None:
        return str(input_arg)
    if input_option is not None:
        return input_option

    if allow_stdin and not sys.stdin.isatty():
        return "-"

    if allow_stdin:
        typer.echo(
            "Error: missing input; pass input argument, use --input <path>, or pipe JSON via stdin.",
            err=True,
        )
    else:
        typer.echo("Error: missing input; pass input argument or --input <path>.", err=True)
    raise typer.Exit(code=ExitCode.USAGE)


def _load_payload(input_source: str) -> dict[str, object]:
    try:
        if input_source == "-":
            payload = json.loads(sys.stdin.read())
        else:
            input_path = Path(input_source)
            if not input_path.exists() and input_path.name == "resume.example.json":
                legacy_example_path = Path(__file__).resolve().parents[2] / "examples" / "resume.example.json"
                if legacy_example_path.exists():
                    input_path = legacy_example_path
            payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        typer.echo(
            f"Error: input must be valid JSON ({exc.msg}).",
            err=True,
        )
        raise typer.Exit(code=ExitCode.JSON_PARSE) from exc
    except OSError as exc:
        typer.echo(
            f"Error: I/O error while reading input '{input_source}': {exc}",
            err=True,
        )
        raise typer.Exit(code=ExitCode.IO) from exc

    if not isinstance(payload, dict):
        typer.echo("Error: JSON root must be an object", err=True)
        raise typer.Exit(code=ExitCode.JSON_PARSE)
    return payload


def _write_output(output: str, output_path: str) -> None:
    try:
        if output_path == "-":
            typer.echo(output, nl=False)
            return

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")
    except OSError as exc:
        typer.echo(
            f"Error: I/O error while writing output '{output_path}': {exc}",
            err=True,
        )
        raise typer.Exit(code=ExitCode.IO) from exc


def _run_convert(input_source: str, output_path: str) -> None:
    try:
        payload = _load_payload(input_source)
        yaml_output = dump_rendercv_yaml(convert_jsonresume_to_rendercv(payload))
        _write_output(yaml_output, output_path)
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"Error: unexpected error: {exc}", err=True)
        raise typer.Exit(code=ExitCode.UNEXPECTED) from exc


def _run_render_html(input_yaml_path: str, html_output_path: str) -> None:
    input_yaml = Path(input_yaml_path)
    if not input_yaml.exists():
        typer.echo(
            f"Error: I/O error while reading input '{input_yaml_path}': file not found",
            err=True,
        )
        raise typer.Exit(code=ExitCode.IO)

    if input_yaml.suffix.lower() == ".json":
        typer.echo(
            "Error: render-html expects RenderCV YAML input, not JSON Resume. "
            "Use 'profilectl html' or run 'profilectl convert' first.",
            err=True,
        )
        raise typer.Exit(code=ExitCode.USAGE)

    output_html = Path(html_output_path)
    output_html.parent.mkdir(parents=True, exist_ok=True)
    markdown_tmp = output_html.with_suffix(f"{output_html.suffix}.md.tmp")

    command = [
        "rendercv",
        "render",
        str(input_yaml),
        "--markdown-path",
        str(markdown_tmp.resolve()),
        "--html-path",
        str(output_html.resolve()),
        "--dont-generate-pdf",
        "--dont-generate-png",
        "--dont-generate-typst",
        "--quiet",
    ]

    try:
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
        except FileNotFoundError as exc:
            typer.echo("Error: 'rendercv' command not found. Install RenderCV first.", err=True)
            raise typer.Exit(code=ExitCode.UNEXPECTED) from exc
        except OSError as exc:
            typer.echo(f"Error: I/O error while running rendercv: {exc}", err=True)
            raise typer.Exit(code=ExitCode.IO) from exc

        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            if not detail:
                fallback_command = [item for item in command if item != "--quiet"]
                fallback_result = subprocess.run(
                    fallback_command,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                detail = (fallback_result.stderr or fallback_result.stdout).strip()
            if not detail:
                detail = "unknown error"
            typer.echo(f"Error: rendercv render failed: {detail}", err=True)
            raise typer.Exit(code=ExitCode.UNEXPECTED)
    finally:
        try:
            markdown_tmp.unlink(missing_ok=True)
        except OSError:
            pass


def _run_validate(input_path: Path) -> None:
    try:
        errors = validate_jsonresume(input_path)
    except json.JSONDecodeError as exc:
        typer.echo(f"Error: input must be valid JSON ({exc.msg}).", err=True)
        raise typer.Exit(code=ExitCode.JSON_PARSE) from exc
    except OSError as exc:
        typer.echo(f"Error: I/O error while reading input '{input_path}': {exc}", err=True)
        raise typer.Exit(code=ExitCode.IO) from exc

    if errors:
        for error in errors:
            typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=ExitCode.JSON_PARSE)


@app.command(
    short_help="Convert JSON Resume to RenderCV YAML.",
    help=(
        "Convert input JSON Resume to RenderCV YAML.\n\n"
        "Examples:\n"
        "  profilectl convert examples/resume.example.json\n"
        "  profilectl convert -i examples/resume.example.json -o output/rendercv_CV.yaml\n"
        "  cat examples/resume.example.json | profilectl convert"
    )
)
def convert(
    input: Annotated[
        Path | None,
        typer.Argument(help="Input file path."),
    ] = None,
    input_option: Annotated[
        str | None,
        typer.Option(
            "--input",
            "-i",
            help="Input file path (alternative to positional).",
        ),
    ] = None,
    output_path: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output RenderCV YAML file path. Use '-' for stdout.",
        ),
    ] = "-",
) -> None:
    input_source = _resolve_input_source(input, input_option, allow_stdin=True)
    _run_convert(input_source=input_source, output_path=output_path)


@app.command(hidden=True)
def rendercv(
    input: Annotated[Path, typer.Argument(help="Input file path.")],
    output_path: Annotated[
        str,
        typer.Option("--out", "-o", help="Output path; defaults to stdout."),
    ] = "-",
) -> None:
    """Compatibility alias for the convert command."""
    _run_convert(input_source=str(input), output_path=output_path)


@app.command(
    "render-html",
    short_help="Render HTML from RenderCV YAML.",
    help=(
        "Render input RenderCV YAML to an HTML file.\n\n"
        "Examples:\n"
        "  profilectl render-html output/rendercv_CV.yaml -o output/index.html\n"
        "  profilectl render-html -i output/rendercv_CV.yaml"
    ),
)
def render_html(
    input: Annotated[
        Path | None,
        typer.Argument(help="Input file path."),
    ] = None,
    input_option: Annotated[
        str | None,
        typer.Option(
            "--input",
            "-i",
            help="Input file path (alternative to positional).",
        ),
    ] = None,
    output_path: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output HTML file path.",
        ),
    ] = "output/index.html",
) -> None:
    input_source = _resolve_input_source(input, input_option, allow_stdin=False)
    if output_path == "-":
        typer.echo("Error: output path for render-html cannot be stdout ('-').", err=True)
        raise typer.Exit(code=ExitCode.USAGE)

    _run_render_html(input_yaml_path=input_source, html_output_path=output_path)


@app.command(
    short_help="Run validate, convert, and render-html.",
    help=(
        "Run the full pipeline from input JSON Resume to HTML.\n\n"
        "Pipeline:\n"
        "1) validate input JSON Resume\n"
        "2) convert to RenderCV YAML\n"
        "3) render HTML from RenderCV YAML\n\n"
        "Examples:\n"
        "  profilectl html examples/resume.example.json\n"
        "  profilectl html -i ../profile-data/data/resume.json -o output/rendercv_CV.yaml --html-output output/index.html"
    ),
)
def html(
    input: Annotated[
        Path | None,
        typer.Argument(help="Input file path."),
    ] = None,
    input_path: Annotated[
        str | None,
        typer.Option("--input", "-i", help="Input file path (alternative to positional)."),
    ] = None,
    output_path: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output RenderCV YAML file path.",
        ),
    ] = "output/rendercv_CV.yaml",
    html_output_path: Annotated[
        str,
        typer.Option(
            "--html-output",
            help="Output HTML file path.",
        ),
    ] = "output/index.html",
) -> None:
    input_source = _resolve_input_source(input, input_path, allow_stdin=False)
    if output_path == "-":
        typer.echo("Error: output path for html cannot be stdout ('-').", err=True)
        raise typer.Exit(code=ExitCode.USAGE)
    if html_output_path == "-":
        typer.echo("Error: html output path for html cannot be stdout ('-').", err=True)
        raise typer.Exit(code=ExitCode.USAGE)

    _run_validate(Path(input_source))

    _run_convert(input_source=input_source, output_path=output_path)
    _run_render_html(input_yaml_path=output_path, html_output_path=html_output_path)


@app.command(
    help=(
        "Validate input JSON Resume against the project schema.\n\n"
        "Examples:\n"
        "  profilectl validate examples/resume.example.json\n"
        "  profilectl validate -i ../profile-data/data/resume.json"
    )
)
def validate(
    input: Annotated[
        Path | None,
        typer.Argument(help="Input file path."),
    ] = None,
    input_path: Annotated[
        str | None,
        typer.Option("--input", "-i", help="Input file path (alternative to positional)."),
    ] = None,
) -> None:
    input_source = _resolve_input_source(input, input_path, allow_stdin=False)
    _run_validate(Path(input_source))

    typer.echo("OK")
