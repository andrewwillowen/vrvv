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
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Path to a CFOUR output file.",
        ),
    ],
) -> None:
    """Use the CFOUR parsing plugin."""
    load_builtin_parsers()
    parser = get_parser("cfour")
    logger.info("Invoking parser '{}' for '{}'.", parser.name, path)
    try:
        raw_data = parser.parse_raw(path)
        normalize_cfour_data(raw_data)
    except NotImplementedError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
