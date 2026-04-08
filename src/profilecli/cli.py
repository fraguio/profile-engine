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
        "CLI para validar y convertir perfiles JSON Resume.\n\n"
        "Entrada/salida para convert:\n"
        "- stdin: -i - o --input -\n"
        "- stdout: por defecto, o explicitamente -o - / --output -\n"
        "- fichero: -o <ruta> o --output <ruta>\n\n"
        "### Validar datos de entrada\n"
        "profilectl validate examples/resume.example.json\n\n"
        "### Convertir (salida por stdout)\n"
        "Por defecto, la salida se escribe en stdout:\n"
        "profilectl convert examples/resume.example.json\n\n"
        "### Convertir a fichero\n"
        "profilectl convert examples/resume.example.json -o out.yaml\n\n"
        "### Convertir desde stdin\n"
        "cat examples/resume.example.json | profilectl convert -i -"
    ),
)
SUPPORTED_CONVERT_FORMAT = "rendercv"


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


def _resolve_input_source(input_path: Path | None, input_option: str | None) -> str:
    if input_path is not None and input_option is not None:
        typer.echo("Error: pass either PATH or --input, not both.", err=True)
        raise typer.Exit(code=ExitCode.USAGE)
    if input_path is not None:
        return str(input_path)
    if input_option is not None:
        return input_option
    if sys.stdin.isatty():
        typer.echo(
            "Error: missing input; pass PATH, use --input <path>, or pipe JSON via stdin.",
            err=True,
        )
        raise typer.Exit(code=ExitCode.USAGE)
    return "-"


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


def _run_convert(input_source: str, output_path: str, fmt: str) -> None:
    if fmt != SUPPORTED_CONVERT_FORMAT:
        typer.echo(
            f"Error: unsupported format '{fmt}'. Allowed value: '{SUPPORTED_CONVERT_FORMAT}'.",
            err=True,
        )
        raise typer.Exit(code=ExitCode.USAGE)

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

    output_html = Path(html_output_path)
    output_html.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "rendercv",
        "render",
        str(input_yaml),
        "--html-path",
        str(output_html.resolve()),
        "--dont-generate-pdf",
        "--dont-generate-png",
        "--dont-generate-typst",
        "--quiet",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        typer.echo("Error: 'rendercv' command not found. Install RenderCV first.", err=True)
        raise typer.Exit(code=ExitCode.UNEXPECTED) from exc
    except OSError as exc:
        typer.echo(f"Error: I/O error while running rendercv: {exc}", err=True)
        raise typer.Exit(code=ExitCode.IO) from exc

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "unknown error").strip()
        typer.echo(f"Error: rendercv render failed: {detail}", err=True)
        raise typer.Exit(code=ExitCode.UNEXPECTED)


@app.command(
    short_help="Convert JSON Resume to RenderCV YAML.",
    help=(
        "Convert JSON Resume to RenderCV YAML.\n\n"
        "Input:\n"
        "- PATH como argumento posicional, o\n"
        "- -i/--input para ruta explicita, o\n"
        "- -i - / --input - para leer desde stdin\n\n"
        "Output:\n"
        "- por defecto stdout, o\n"
        "- -o/--output para escribir a fichero, o\n"
        "- -o - / --output - para forzar stdout\n\n"
        "Examples:\n"
        "  profilectl convert examples/resume.example.json\n"
        "  profilectl convert examples/resume.example.json -o out.yaml\n"
        "  cat examples/resume.example.json | profilectl convert -i -"
    )
)
def convert(
    path: Annotated[
        Path | None,
        typer.Argument(help="Input JSON Resume file path."),
    ] = None,
    input_option: Annotated[
        str | None,
        typer.Option(
            "--input",
            "-i",
            help="Input file path, or '-' to read from stdin.",
        ),
    ] = None,
    output_path: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output file path (default: '-'; write to stdout).",
        ),
    ] = "-",
    fmt: Annotated[
        str,
        typer.Option(
            "--format",
            help="Output format. Supported value: 'rendercv'.",
        ),
    ] = "rendercv",
) -> None:
    """Examples:

    - profilectl convert examples/resume.example.json
    - profilectl convert examples/resume.example.json -o out.yaml
    - cat examples/resume.example.json | profilectl convert -i -
    """
    input_source = _resolve_input_source(path, input_option)
    _run_convert(input_source=input_source, output_path=output_path, fmt=fmt)


@app.command(hidden=True)
def rendercv(
    input_path: Annotated[Path, typer.Argument(help="Input JSON Resume path.")],
    output_path: Annotated[
        str,
        typer.Option("--out", "-o", help="Output path; defaults to stdout."),
    ] = "-",
) -> None:
    """Compatibility alias for the convert command."""
    _run_convert(input_source=str(input_path), output_path=output_path, fmt="rendercv")


@app.command("render-html", short_help="Render HTML from RenderCV YAML.")
def render_html(
    input_path: Annotated[
        Path,
        typer.Argument(help="Input RenderCV YAML file path."),
    ],
    output_path: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output HTML file path.",
        ),
    ] = "output/index.html",
) -> None:
    if output_path == "-":
        typer.echo("Error: output path for render-html cannot be stdout ('-').", err=True)
        raise typer.Exit(code=ExitCode.USAGE)

    _run_render_html(input_yaml_path=str(input_path), html_output_path=output_path)


@app.command(short_help="Validate, convert, and render HTML in one command.")
def html(
    path: Annotated[
        Path | None,
        typer.Argument(help="Input JSON Resume path."),
    ] = None,
    input_path: Annotated[
        Path | None,
        typer.Option("--in", help="Input JSON Resume path."),
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
    if path is not None and input_path is not None:
        typer.echo("Error: pass either PATH or --in, not both.", err=True)
        raise typer.Exit(code=ExitCode.USAGE)
    if path is None and input_path is None:
        typer.echo("Error: missing input path; pass PATH or --in.", err=True)
        raise typer.Exit(code=ExitCode.USAGE)
    if output_path == "-":
        typer.echo("Error: output path for html cannot be stdout ('-').", err=True)
        raise typer.Exit(code=ExitCode.USAGE)
    if html_output_path == "-":
        typer.echo("Error: html output path for html cannot be stdout ('-').", err=True)
        raise typer.Exit(code=ExitCode.USAGE)

    resolved_input_path = path if path is not None else input_path
    assert resolved_input_path is not None

    try:
        errors = validate_jsonresume(resolved_input_path)
    except json.JSONDecodeError as exc:
        typer.echo(f"Error: input must be valid JSON ({exc.msg}).", err=True)
        raise typer.Exit(code=ExitCode.JSON_PARSE) from exc
    except OSError as exc:
        typer.echo(f"Error: I/O error while reading input '{resolved_input_path}': {exc}", err=True)
        raise typer.Exit(code=ExitCode.IO) from exc

    if errors:
        for error in errors:
            typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=ExitCode.JSON_PARSE)

    _run_convert(input_source=str(resolved_input_path), output_path=output_path, fmt="rendercv")
    _run_render_html(input_yaml_path=output_path, html_output_path=html_output_path)


@app.command()
def validate(
    path: Annotated[
        Path | None,
        typer.Argument(help="Input JSON Resume path."),
    ] = None,
    input_path: Annotated[
        Path | None,
        typer.Option("--in", help="Input JSON Resume path."),
    ] = None,
) -> None:
    if path is not None and input_path is not None:
        typer.echo("Error: pass either PATH or --in, not both.", err=True)
        raise typer.Exit(code=ExitCode.USAGE)
    if path is None and input_path is None:
        typer.echo("Error: missing input path; pass PATH or --in.", err=True)
        raise typer.Exit(code=ExitCode.USAGE)

    resolved_input_path = path if path is not None else input_path
    assert resolved_input_path is not None

    try:
        errors = validate_jsonresume(resolved_input_path)
    except json.JSONDecodeError as exc:
        typer.echo(f"Error: input must be valid JSON ({exc.msg}).", err=True)
        raise typer.Exit(code=ExitCode.JSON_PARSE) from exc
    except OSError as exc:
        typer.echo(f"Error: I/O error while reading input '{resolved_input_path}': {exc}", err=True)
        raise typer.Exit(code=ExitCode.IO) from exc

    if errors:
        for error in errors:
            typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=ExitCode.JSON_PARSE)

    typer.echo("OK")
