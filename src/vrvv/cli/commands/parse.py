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
    to_csv: Annotated[
        Path | None,
        typer.Option(
            "--to-csv",
            help="Export normalized data as CSV files in this directory.",
            file_okay=False,
            writable=True,
        ),
    ] = None,
    to_dat: Annotated[
        Path | None,
        typer.Option(
            "--to-dat",
            help="Export normalized data as a legacy Fortran DAT file.",
            dir_okay=False,
            writable=True,
        ),
    ] = None,
    to_excel: Annotated[
        Path | None,
        typer.Option(
            "--to-excel",
            help="Export normalized data to worksheets in an Excel workbook.",
            dir_okay=False,
            writable=True,
        ),
    ] = None,
) -> None:
    """Use the CFOUR parsing plugin."""

    load_builtin_parsers()
    parser = get_parser("cfour")
    logger.info("Invoking parser '{}' for '{}'.", parser.name, path)

    can_parse_strict = parser.can_parse(path, strict=True)
    logger.debug("Able to validate input strictly: {}", can_parse_strict)
    if not can_parse_strict:
        typer.echo("CFOUR parser could not find all required files.", err=True)
        raise typer.Exit(code=1)

    try:
        raw_data = parser.parse_raw(path)
        standard_data = normalize_cfour_data(raw_data)
        if to_csv is not None:
            standard_data.to_csv(to_csv)
        if to_dat is not None:
            standard_data.to_dat(to_dat)
        if to_excel is not None:
            standard_data.to_excel(to_excel)
    except (NotImplementedError, OSError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
