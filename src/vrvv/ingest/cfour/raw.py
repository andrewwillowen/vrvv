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
    pass


@dc.dataclass(slots=True)
class RawCFOURdidQ:
    pass


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
