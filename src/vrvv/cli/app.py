"""
Main Typer entrypoint for vrvv CLI
"""

from typing import Annotated

import typer

from vrvv.__about__ import __version__
from vrvv.cli.commands.parse import app as parse_app
from vrvv.logging import configure_logging

app = typer.Typer(no_args_is_help=True)


# Add global flags
@app.callback()
def cli_callback(
    verbose: Annotated[  # noqa: FBT002
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable debug logging.",
        ),
    ] = False,
) -> None:
    level = "DEBUG" if verbose else "INFO"
    configure_logging(level=level)


# Subcommands
app.add_typer(parse_app, name="parse")


# Top level commands
@app.command()
def version() -> None:
    """Report installed vrvv version."""
    typer.echo(__version__)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
