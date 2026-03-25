from __future__ import annotations

import json
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


app = typer.Typer(add_completion=False, no_args_is_help=True)
SUPPORTED_EXPORT_FORMAT = "rendercv"


def _print_version(value: bool) -> None:
    if not value:
        return
    try:
        resolved_version = version("cvtool")
    except PackageNotFoundError:
        try:
            resolved_version = version("cv-automation")
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


def _resolve_input_source(input_path: Path | None, input_option: str) -> str:
    if input_path is not None and input_option != "-":
        typer.echo("Error: pass either PATH or --input, not both.", err=True)
        raise typer.Exit(code=ExitCode.USAGE)
    if input_path is not None:
        return str(input_path)
    return input_option


def _load_payload(input_source: str) -> dict[str, object]:
    try:
        if input_source == "-":
            payload = json.loads(sys.stdin.read())
        else:
            payload = json.loads(Path(input_source).read_text(encoding="utf-8"))
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


def _run_export(input_source: str, output_path: str, fmt: str) -> None:
    if fmt != SUPPORTED_EXPORT_FORMAT:
        typer.echo(
            f"Error: unsupported format '{fmt}'. Allowed value: '{SUPPORTED_EXPORT_FORMAT}'.",
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


@app.command(
    help=(
        "Export a JSON Resume to RenderCV YAML. "
        "Use '-' for stdin/stdout."
    )
)
def export(
    path: Annotated[
        Path | None,
        typer.Argument(help="Input JSON Resume file path."),
    ] = None,
    input_option: Annotated[
        str,
        typer.Option(
            "--input",
            "-i",
            help="Input file path (default: '-'; read from stdin).",
        ),
    ] = "-",
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

    - cvtool export resume.example.json -o -
    - cvtool export -i - -o out.yaml
    """
    input_source = _resolve_input_source(path, input_option)
    _run_export(input_source=input_source, output_path=output_path, fmt=fmt)


@app.command(hidden=True)
def rendercv(
    input_path: Annotated[Path, typer.Argument(help="Input JSON Resume path.")],
    output_path: Annotated[
        str,
        typer.Option("--out", "-o", help="Output path; defaults to stdout."),
    ] = "-",
) -> None:
    """Compatibility alias for the export command."""
    _run_export(input_source=str(input_path), output_path=output_path, fmt="rendercv")


@app.command()
def validate(
    input_path: Annotated[Path, typer.Option("--in", help="Input JSON Resume path.")],
) -> None:
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

    typer.echo("OK")
