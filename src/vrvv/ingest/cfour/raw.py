"""Typed dataclasses for holding CFOUR-specific raw data."""

import dataclasses as dc
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


@dc.dataclass(slots=True)
class RawDataCFOUR:
    """Source-faithful data parsed from a CFOUR anharmonic calculation."""

    source_path: Path
    anharm: "RawCFOURAnharm"
    zetas: "RawCFOURZetas"
    cubic: "RawCFOURCubic"
    didq: "RawCFOURdidQ"


@dc.dataclass(slots=True)
class RawRotationalConstants:
    """CFOUR equilibrium rotational constants (Be), in MHz."""

    X: float
    Y: float
    Z: float


@dc.dataclass(slots=True)
class RawHarmonicFrequencies:
    """CFOUR harmonic frequencies in wavenumbers (cm^-1).

    Values retain CFOUR's original mode indexing; the lowest-energy
    vibrational mode normally has index 7.
    """

    by_index: dict[int, float] = dc.field(default_factory=dict)
    first_mode_index: int = 7


@dc.dataclass(slots=True)
class RawCFOURAnharm:
    """Source-faithful quantities parsed from CFOUR's ``anharm.out`` file."""

    equilibrium_rotational_constants: RawRotationalConstants
    harmonic_frequencies: RawHarmonicFrequencies
    n_atoms: int
    is_linear: bool


@dc.dataclass(slots=True)
class RawCFOURCubic:
    """Source-faithful cubic force constants from ``cubic``, in cm^-1."""

    # CFOUR mode numbers, retained as one-indexed values from the source file.
    # Only permutation-unique entries are stored, matching the CFOUR file layout.
    mode_indices: NDArray[np.int64]
    values: NDArray[np.float64]


@dc.dataclass(slots=True)
class RawCFOURdidQ:
    """Source-faithful inertial derivatives from ``didQ``, in sqrt(amu) * bohr."""

    # First two indices are Cartesian axis components (one-indexed, 1-3);
    # the third is the CFOUR mode number (one-indexed, from 7).
    # All entries present in the source file are stored, matching the CFOUR
    # file layout (no reduction to a permutation-unique or triangular subset).
    mode_indices: NDArray[np.int64]
    values: NDArray[np.float64]


@dc.dataclass(slots=True)
class RawCFOURZetas:
    """Source-faithful, dimensionless Coriolis zeta data for three axes."""

    axis1: "RawZetasSection"
    axis2: "RawZetasSection"
    axis3: "RawZetasSection"


@dc.dataclass(slots=True)
class RawZetasSection:
    """Dimensionless lower-triangular Coriolis zeta entries for one axis."""

    # CFOUR mode numbers, retained as one-indexed values from the source file.
    mode_indices: NDArray[np.int64]
    values: NDArray[np.float64]
