"""Read CFOUR files and return a CFOUR-specific raw object."""

from pathlib import Path

from loguru import logger

from vrvv.ingest.base import ParserPlugin
from vrvv.ingest.cfour.raw import (
    RawCFOURAnharm,
    RawCFOURCubic,
    RawCFOURdidQ,
    RawCFOURZetas,
    RawDataCFOUR,
)


def parse_anharm_out(path: Path) -> RawCFOURAnharm:
    """Parses data from the 'anharm.out' file."""


def parse_zetas(path: Path) -> RawCFOURZetas:
    """Parses data from the 'corioliszeta' file."""


def parse_cubic(path: Path) -> RawCFOURCubic:
    """Parses data from the 'cubic' file."""


def parse_didQ(path: Path) -> RawCFOURdidQ:  # noqa: N802
    """Parses data from the 'didQ' file."""


class CFOURParser(ParserPlugin):
    """Minimal scaffold parser plugin for CFOUR files."""

    name = "cfour"

    def can_parse(self, path: Path, *, strict: bool = True) -> bool:
        """
        Checks that the provided path is a directory that contains
        the files:

        * anharm.out
        * corioliszeta
        * cubic
        * didQ

        """
        if (not path.exists()) or (not path.is_dir()):
            logger.debug("CFOUR can_parse path='{}' | not a directory.", path)
            return False

        logger.debug("CFOUR can_parse path='{}' | is a directory.", path)

        file_dict: dict = dict.fromkeys(("anharm.out", "corioliszeta", "cubic", "didQ"), False)

        for key in file_dict:
            file_path = path / key
            path_exists = file_path.exists()
            path_is_file = file_path.is_file()
            file_dict[key] = path_exists and path_is_file
            logger.debug(
                "CFOUR can_parse path='{}' | exists={} is_file={}.",
                file_path,
                path_exists,
                path_is_file,
            )

        if all(i for i in file_dict.values()):
            logger.debug("CFOUR can_parse path='{}' matched=True.", path)
            return True

        if (not strict) and any(i for i in file_dict.values()):
            logger.debug("CFOUR can_parse path='{}' matched=True strict={}.", path, strict)
            return True

        logger.debug("CFOUR can_parse path='{}' matched=False.", path)
        return False

    def parse_raw(self, path: Path) -> RawDataCFOUR:
        logger.info("CFOUR parse requested for '{}'.", path)
        message = f"CFOUR parsing logic is not implemented yet for path: {path}"
        raise NotImplementedError(message)


CFOUR_PLUGIN = CFOURParser()
