"""Read CFOUR files and return a CFOUR-specific raw object."""

import re
from pathlib import Path

import numpy as np
from loguru import logger

from vrvv.ingest.base import ParserPlugin
from vrvv.ingest.cfour._textparse import (
    extract_section,
    iter_data_lines,
    parse_indexed_value_row,
    parse_labeled_float_row,
)
from vrvv.ingest.cfour.raw import (
    RawCFOURAnharm,
    RawCFOURCubic,
    RawCFOURdidQ,
    RawCFOURZetas,
    RawDataCFOUR,
    RawHarmonicFrequencies,
    RawRotationalConstants,
    RawZetasSection,
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
    return RawRotationalConstants(*be_values_mhz)


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

    if not harmonics_wn:
        raise ValueError("CFOUR harmonic frequencies are empty")
    return RawHarmonicFrequencies(
        by_index=harmonics_wn, first_mode_index=min(harmonics_wn)
    )


def parse_atom_count(text: str) -> int:
    """Extract the molecular atom count reported by CFOUR's geometry reader."""
    match = re.search(r"@GETXYZ-I,\s+(\d+)\s+atoms read from ZMAT\.", text)
    if match is None:
        raise ValueError("CFOUR anharm.out does not report an atom count")
    return int(match.group(1))


def _classify_molecule(n_atoms: int, n_modes: int, first_mode_index: int) -> bool:
    """Classify molecular geometry from CFOUR's atom and mode counts."""
    nonlinear_modes = 3 * n_atoms - 6
    linear_modes = 3 * n_atoms - 5
    if n_modes == nonlinear_modes and first_mode_index == 7:
        return False
    if n_modes == linear_modes and first_mode_index == 6:
        return True
    raise ValueError(
        "CFOUR harmonic mode layout is inconsistent with atom count: "
        f"n_atoms={n_atoms}, n_modes={n_modes}, first_mode_index={first_mode_index}"
    )


def parse_anharm_out(path: Path) -> RawCFOURAnharm:
    """Parses data from the 'anharm.out' file."""
    anharm_file = path.read_text()

    harmonic_frequencies = parse_harmonic_frequencies(anharm_file)
    n_atoms = parse_atom_count(anharm_file)
    is_linear = _classify_molecule(
        n_atoms,
        len(harmonic_frequencies.by_index),
        harmonic_frequencies.first_mode_index,
    )

    return RawCFOURAnharm(
        equilibrium_rotational_constants=parse_rotational_constants(anharm_file),
        harmonic_frequencies=harmonic_frequencies,
        n_atoms=n_atoms,
        is_linear=is_linear,
    )


def parse_zetas_by_section(section: str) -> RawZetasSection:
    """Parse one CFOUR Coriolis zeta lower-triangular matrix section."""

    zetas_lines = list(iter_data_lines(section))
    if not zetas_lines:
        message = "Coriolis zeta section is empty!"
        raise ValueError(message)

    mode_indices = np.empty((len(zetas_lines), 2), dtype=np.int64)
    values = np.empty(len(zetas_lines), dtype=np.float64)
    for row, line in enumerate(zetas_lines):
        indices, (value,) = parse_indexed_value_row(
            line, n_indices=2, n_values=1, make_zero_indexed=False
        )
        mode_indices[row] = indices
        values[row] = value

    return RawZetasSection(mode_indices=mode_indices, values=values)


def parse_zetas(path: Path) -> RawCFOURZetas:
    """Parse source-faithful Coriolis zeta data from a 'corioliszeta' file."""
    corioliszeta_file = path.read_text()

    axis1_text = extract_section(
        corioliszeta_file,
        "Coriolis Zeta matrix for IXYZ=                     1 :",
        "Coriolis Zeta matrix for IXYZ=                     2 :",
    )

    axis2_text = extract_section(
        corioliszeta_file,
        "Coriolis Zeta matrix for IXYZ=                     2 :",
        "Coriolis Zeta matrix for IXYZ=                     3 :",
    )

    axis3_text = extract_section(
        corioliszeta_file,
        "Coriolis Zeta matrix for IXYZ=                     3 :",
        None,
    )

    return RawCFOURZetas(
        axis1=parse_zetas_by_section(axis1_text),
        axis2=parse_zetas_by_section(axis2_text),
        axis3=parse_zetas_by_section(axis3_text),
    )


def parse_cubic(path: Path) -> RawCFOURCubic:
    """Parse source-faithful cubic force constants from a 'cubic' file."""
    cubic_lines = list(iter_data_lines(path.read_text()))
    if not cubic_lines:
        message = "Cubic force constant file is empty!"
        raise ValueError(message)

    mode_indices = np.empty((len(cubic_lines), 3), dtype=np.int64)
    values = np.empty(len(cubic_lines), dtype=np.float64)
    for row, line in enumerate(cubic_lines):
        indices, (value,) = parse_indexed_value_row(
            line, n_indices=3, n_values=1, make_zero_indexed=False
        )
        mode_indices[row] = indices
        values[row] = value

    return RawCFOURCubic(mode_indices=mode_indices, values=values)


def parse_didQ(path: Path) -> RawCFOURdidQ:
    """Parse source-faithful dipole moment derivatives from a 'didQ' file."""
    didq_lines = list(iter_data_lines(path.read_text()))
    if not didq_lines:
        message = "didQ file is empty!"
        raise ValueError(message)

    mode_indices = np.empty((len(didq_lines), 3), dtype=np.int64)
    values = np.empty(len(didq_lines), dtype=np.float64)
    for row, line in enumerate(didq_lines):
        indices, (value,) = parse_indexed_value_row(
            line, n_indices=3, n_values=1, make_zero_indexed=False
        )
        mode_indices[row] = indices
        values[row] = value

    return RawCFOURdidQ(mode_indices=mode_indices, values=values)


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
        if not self.can_parse(path, strict=True):
            message = f"CFOUR directory is missing required files: {path}"
            raise ValueError(message)

        return RawDataCFOUR(
            source_path=path,
            anharm=parse_anharm_out(path / "anharm.out"),
            zetas=parse_zetas(path / "corioliszeta"),
            cubic=parse_cubic(path / "cubic"),
            didq=parse_didQ(path / "didQ"),
        )


CFOUR_PLUGIN = CFOURParser()
