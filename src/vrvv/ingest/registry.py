"""
Pluggable parser registry, to support third party data parsing.
"""

from pathlib import Path

from loguru import logger

from vrvv.ingest.base import (
    ParserAutodetectError,
    ParserNotFoundError,
    ParserPlugin,
    ParserRegistryError,
)
from vrvv.ingest.cfour.parser import CFOUR_PLUGIN

_PARSERS: dict[str, ParserPlugin] = {}


def _normalize_name(name: str) -> str:
    return name.strip().lower()


def register_parser(parser: ParserPlugin) -> None:
    """Register a parser plugin by unique name."""
    key = _normalize_name(parser.name)
    if not key:
        message = "Parser name must not be empty."
        raise ParserRegistryError(message)
    if key in _PARSERS:
        message = f"Parser '{key}' is already registered."
        raise ParserRegistryError(message)
    _PARSERS[key] = parser
    logger.info("Registered parser plugin '{}'.", key)


def get_parser(name: str) -> ParserPlugin:
    """Return a parser plugin by name."""
    key = _normalize_name(name)
    try:
        parser = _PARSERS[key]
    except KeyError as exc:
        message = f"Unknown parser '{name}'."
        raise ParserNotFoundError(message) from exc
    logger.debug("Resolved parser '{}' from registry.", key)
    return parser


def list_parsers() -> list[str]:
    """Return sorted registered parser names."""
    return sorted(_PARSERS)


def autodetect_parser(path: Path) -> ParserPlugin:
    """Select parser from can_parse matches."""
    matches = [parser for parser in _PARSERS.values() if parser.can_parse(path)]
    if not matches:
        message = f"No parser matched file: {path}"
        raise ParserAutodetectError(message)
    if len(matches) > 1:
        names = ", ".join(sorted(parser.name for parser in matches))
        message = f"Ambiguous parser autodetect for '{path}': {names}"
        raise ParserAutodetectError(message)
    selected = matches[0]
    logger.info("Autodetected parser '{}' for '{}'.", selected.name, path)
    return selected


def load_builtin_parsers() -> None:
    """Register built-in parser plugins."""
    if "cfour" in _PARSERS:
        logger.debug("Builtin parser 'cfour' already loaded; skipping.")
        return
    register_parser(CFOUR_PLUGIN)
