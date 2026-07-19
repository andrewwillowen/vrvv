"""
Parse computational output files for data necessary for vrvv.
"""

from pathlib import Path
from typing import Annotated

import typer
from loguru import logger

from vrvv.ingest.cfour.normalize import normalize_cfour_data
from vrvv.ingest.registry import get_parser, load_builtin_parsers

app = typer.Typer(
    help="Parse files for necessary data.",
    no_args_is_help=True,
)


@app.command("cfour")
def cfour(
    path: Annotated[
        Path,
        typer.Argument(
            ...,
            exists=True,
            dir_okay=True,
            file_okay=False,
            readable=True,
            resolve_path=True,
            help="Path to a directory containing CFOUR output files.",
        ),
    ],
    strict: Annotated[  # noqa: FBT002
        bool,
        typer.Option(
            "--strict/--no-strict",
            help="All required CFOUR files must be present.",
        ),
    ] = True,
) -> None:
    """Use the CFOUR parsing plugin."""

    load_builtin_parsers()
    parser = get_parser("cfour")
    logger.info("Invoking parser '{}' for '{}'.", parser.name, path)

    can_parse_strict = parser.can_parse(path, strict=True)
    logger.debug("Able to validate input strictly: {}", can_parse_strict)

    can_parse_loose = parser.can_parse(path, strict=False)
    logger.debug("Able to validate input loosely: {}", can_parse_loose)

    # If strict, fail on missing files.
    # If not strict, warn on missing file(s), fail on missing *all* files.
    if strict:
        if not can_parse_strict:
            typer.echo("CFOUR parser could not find required files.", err=True)
            raise typer.Exit(code=1)
    elif (not can_parse_strict) and can_parse_loose:
        logger.warning("CFOUR parser could not find all required files; continuing anyway.")
    elif not can_parse_loose:
        typer.echo("CFOUR parser could not find any of the required files.", err=True)
        raise typer.Exit(code=1)

    try:
        raw_data = parser.parse_raw(path)
        normalize_cfour_data(raw_data)
    except NotImplementedError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
