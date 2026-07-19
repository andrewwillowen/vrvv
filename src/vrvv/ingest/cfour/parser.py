"""Read CFOUR files and return a CFOUR-specific raw object."""

from pathlib import Path

from loguru import logger

from vrvv.ingest.base import ParserPlugin
from vrvv.ingest.cfour.raw import RawDataCFOUR


class CFOURParser(ParserPlugin):
    """Minimal scaffold parser plugin for CFOUR files."""

    name = "cfour"

    def can_parse(self, path: Path) -> bool:
        suffix_match = path.suffix.lower() in {".out", ".log"}
        name_match = "cfour" in path.name.lower()
        matched = suffix_match or name_match
        logger.debug("CFOUR can_parse path='{}' matched={}.", path, matched)
        return matched

    def parse_raw(self, path: Path) -> RawDataCFOUR:
        logger.info("CFOUR parse requested for '{}'.", path)
        message = f"CFOUR parsing logic is not implemented yet for file: {path}"
        raise NotImplementedError(message)


CFOUR_PLUGIN = CFOURParser()
