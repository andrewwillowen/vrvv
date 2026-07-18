from typer.testing import CliRunner
from vrvv.cli.app import app
from vrvv.__about__ import __version__

runner = CliRunner()


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
