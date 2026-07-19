from pathlib import Path

from typer.testing import CliRunner

from vrvv.__about__ import __version__
from vrvv.cli.app import app

runner = CliRunner()
_CFOUR_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "cfour"


def test_root_help_lists_top_level_commands() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "parse" in result.stdout
    assert "version" in result.stdout


def test_version_command_reports_installed_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_parse_help_lists_parse_subcommands() -> None:
    result = runner.invoke(app, ["parse", "--help"])

    assert result.exit_code == 0
    assert "cfour" in result.stdout


def test_cfour_help_documents_placeholder_command() -> None:
    result = runner.invoke(app, ["parse", "cfour", "--help"])

    assert result.exit_code == 0
    assert "Use the CFOUR parsing plugin." in result.stdout


def test_cfour_command_reports_placeholder_not_implemented() -> None:
    result = runner.invoke(app, ["parse", "cfour", str(_CFOUR_FIXTURE_DIR)])

    assert result.exit_code == 1
    output = f"{result.stdout}{result.stderr}"
    assert "not implemented yet" in output


def test_verbose_flag_enables_debug_logging() -> None:
    result = runner.invoke(app, ["--verbose", "version"])

    assert result.exit_code == 0
    assert "DEBUG" in result.stderr
