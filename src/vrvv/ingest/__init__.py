"""
Functions for parsing and standardizing data
needed for vrvv numeric calculations.

Surfaces numeric data in a standard format so
that other vrvv components will function
regardless of the source of the data.

Establishes a plugin system to support ingesting
data from programs not explicitly included in
this package.
"""

from vrvv.ingest.base import (
    ParserAutodetectError,
    ParserNotFoundError,
    ParserPlugin,
    ParserRegistryError,
)
from vrvv.ingest.registry import (
    autodetect_parser,
    get_parser,
    list_parsers,
    load_builtin_parsers,
    register_parser,
)

__all__ = [
    "ParserAutodetectError",
    "ParserNotFoundError",
    "ParserPlugin",
    "ParserRegistryError",
    "autodetect_parser",
    "get_parser",
    "list_parsers",
    "load_builtin_parsers",
    "register_parser",
]
