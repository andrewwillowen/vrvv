"""
Parse computational output files for data necessary for vrvv.
"""

import typer

app = typer.Typer(
    help="Parse files for necessary data.",
    no_args_is_help=True,
)


@app.command("cfour")
def cfour() -> None:
    """Use the CFOUR parsing plugin."""
    typer.echo("This command will invoke the CFOUR parsing plugin.")
