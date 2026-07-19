"""
Parsing protocol and result types.
"""

from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ParserPlugin(Protocol):
    """Contract for ingest parser plugins."""

    name: str

    def can_parse(self, path: Path) -> bool:
        """Return whether this parser likely supports a file."""

    def parse_raw(self, path: Path) -> Any:
        """Parse source output into plugin-specific raw typed objects."""


class ParserRegistryError(ValueError):
    """Raised when parser registry operations fail."""


class ParserNotFoundError(ParserRegistryError):
    """Raised when a requested parser is not registered."""


class ParserAutodetectError(ParserRegistryError):
    """Raised when parser autodetection fails."""
