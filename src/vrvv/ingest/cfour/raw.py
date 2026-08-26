"""Typed dataclasses for holding CFOUR-specific raw data."""

import dataclasses as dc
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


@dc.dataclass(slots=True)
class RawDataCFOUR:
    source_path: Path


@dc.dataclass(slots=True)
class RawRotationalConstants:
    # Be (equilibrium rotational constants) in MHz
    X: float
    Y: float
    Z: float


@dc.dataclass(slots=True)
class RawHarmonicFrequencies:
    # Harmonic frequencies in wavenumbers (cm^-1)
    # Uses original indexing - lowest energy mode has index of 7
    by_index: dict[int, float] = dc.field(default_factory=dict)
    first_mode_index: int = 7


@dc.dataclass(slots=True)
class RawCFOURAnharm:
    # Ingest from anharm.out file
    equilibrium_rotational_constants: RawRotationalConstants
    harmonic_frequencies: RawHarmonicFrequencies


@dc.dataclass(slots=True)
class RawCFOURCubic:
    """Source-faithful cubic force constant entries from the 'cubic' file."""

    # CFOUR mode numbers, retained as one-indexed values from the source file.
    # Only permutation-unique entries are stored, matching the CFOUR file layout.
    mode_indices: NDArray[np.int64]
    values: NDArray[np.float64]


@dc.dataclass(slots=True)
class RawCFOURdidQ:
    """Source-faithful dipole moment derivative entries from the 'didQ' file."""

    # First two indices are Cartesian axis components (one-indexed, 1-3);
    # the third is the CFOUR mode number (one-indexed, from 7).
    # All entries present in the source file are stored, matching the CFOUR
    # file layout (no reduction to a permutation-unique or triangular subset).
    mode_indices: NDArray[np.int64]
    values: NDArray[np.float64]


@dc.dataclass(slots=True)
class RawCFOURZetas:
    axis1: "RawZetasSection"
    axis2: "RawZetasSection"
    axis3: "RawZetasSection"


@dc.dataclass(slots=True)
class RawZetasSection:
    """Source-faithful lower-triangular Coriolis zeta entries for one axis section."""

    # CFOUR mode numbers, retained as one-indexed values from the source file.
    mode_indices: NDArray[np.int64]
    values: NDArray[np.float64]
