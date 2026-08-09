"""Read CFOUR files and return a CFOUR-specific raw object."""

from pathlib import Path

from loguru import logger

from vrvv.ingest.base import ParserPlugin
from vrvv.ingest.cfour.raw import (
    RawRotationalConstants,
    RawHarmonicFrequencies,
    RawCFOURAnharm,
    RawCFOURCubic,
    RawCFOURdidQ,
    RawCFOURZetas,
    RawDataCFOUR,
)
from vrvv.ingest.cfour._textparse import (
    extract_section,
    iter_data_lines,
    parse_indexed_value_row,
    parse_labeled_float_row,
)


def parse_rotational_constants(text: str) -> RawRotationalConstants:
    """Parse the equilibrium rotational constants"""
    rotational_constants_section = extract_section(
        text,
        "Be, B0 AND B-B0 SHIFTS FOR SINGLY EXCITED VIBRATIONAL STATES (MHz)",
        "Vibrationally averaged dipole moment",
    )
    rotational_constants_lines = list(
        iter_data_lines(rotational_constants_section, skip_prefixes=("VIB",))
    )
    _be_label, be_values_mhz = parse_labeled_float_row(
        rotational_constants_lines[0], n_values=3
    )
    result = RawRotationalConstants(*be_values_mhz)
    return result


def parse_harmonic_frequencies(text: str) -> RawHarmonicFrequencies:
    """Parse the harmonic vibrational frequencies"""
    harmonics_section = extract_section(
        text,
        "HARMONIC AND FUNDAMENTAL FREQUENCIES (cm-1) AND INTENSITIES (km/mol)",
        "ZERO-POINT VIBRATIONAL ENERGIES",
    )
    harmonics_lines = list(
        iter_data_lines(harmonics_section, skip_prefixes=("Har", "Mod"))
    )
    harmonics_wn: dict[int, float] = {}
    for line in harmonics_lines:
        index, values = parse_indexed_value_row(
            line, n_indices=1, n_values=6, make_zero_indexed=False
        )
        harmonics_wn[index[0]] = values[0]

    result = RawHarmonicFrequencies(by_index=harmonics_wn)
    return result


def parse_anharm_out(path: Path) -> RawCFOURAnharm:
    """Parses data from the 'anharm.out' file."""
    with open(path, "r") as f:
        anharm_file = f.read()

    return RawCFOURAnharm(
        equilibrium_rotational_constants=parse_rotational_constants(anharm_file),
        harmonic_frequencies=parse_harmonic_frequencies(anharm_file),
    )


def parse_zetas(path: Path) -> RawCFOURZetas:
    """Parses data from the 'corioliszeta' file."""
    message = f"CFOUR corioliszeta parsing is not implemented yet for path: {path}"
    raise NotImplementedError(message)


def parse_cubic(path: Path) -> RawCFOURCubic:
    """Parses data from the 'cubic' file."""
    message = f"CFOUR cubic parsing is not implemented yet for path: {path}"
    raise NotImplementedError(message)


def parse_didQ(path: Path) -> RawCFOURdidQ:  # noqa: N802
    """Parses data from the 'didQ' file."""
    message = f"CFOUR didQ parsing is not implemented yet for path: {path}"
    raise NotImplementedError(message)


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

        file_dict: dict = dict.fromkeys(
            ("anharm.out", "corioliszeta", "cubic", "didQ"), False
        )

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
            logger.debug(
                "CFOUR can_parse path='{}' matched=True strict={}.", path, strict
            )
            return True

        logger.debug("CFOUR can_parse path='{}' matched=False.", path)
        return False

    def parse_raw(self, path: Path) -> RawDataCFOUR:
        logger.info("CFOUR parse requested for '{}'.", path)
        message = f"CFOUR parsing logic is not implemented yet for path: {path}"
        raise NotImplementedError(message)


CFOUR_PLUGIN = CFOURParser()
