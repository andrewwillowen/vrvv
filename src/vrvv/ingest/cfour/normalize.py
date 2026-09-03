"""Standardize source-faithful CFOUR data into core quantities."""

import itertools

import numpy as np
from loguru import logger
from numpy.typing import NDArray

from vrvv.core.quantities import (
    CoriolisZetas,
    CubicForceConstants,
    EquilibriumRotationalConstants,
    HarmonicFrequencies,
    InertialDerivatives,
    RotationalDerivatives,
    StandardData,
)
from vrvv.core.units import (
    INERTIAL_DERIVATIVE_TO_SI,
    MHZ_TO_HZ,
    PLANCK_CONSTANT_J_S,
    REDUCED_PLANCK_CONSTANT_J_S,
    WAVENUMBER_TO_HZ,
)
from vrvv.ingest.cfour.raw import (
    RawCFOURCubic,
    RawCFOURdidQ,
    RawCFOURZetas,
    RawDataCFOUR,
    RawHarmonicFrequencies,
    RawZetasSection,
)


def _mode_indices(raw: RawHarmonicFrequencies) -> tuple[NDArray[np.int64], int]:
    """Return contiguous CFOUR vibrational indices and their first source index."""
    if not raw.by_index:
        raise ValueError("CFOUR harmonic frequencies are empty")

    indices = np.array(sorted(raw.by_index), dtype=np.int64)
    if indices[0] != raw.first_mode_index:
        raise ValueError(
            "CFOUR harmonic frequencies must begin at "
            f"first_mode_index={raw.first_mode_index}, got {indices[0]}"
        )
    expected = np.arange(raw.first_mode_index, raw.first_mode_index + len(indices))
    if not np.array_equal(indices, expected):
        raise ValueError("CFOUR harmonic frequency indices must be contiguous")
    return indices, raw.first_mode_index


def _normalized_mode_index(
    source_index: int, first_mode_index: int, n_modes: int, quantity: str
) -> int:
    """Validate and convert a CFOUR source mode index to a core mode index."""
    normalized_index = source_index - first_mode_index
    if not 0 <= normalized_index < n_modes:
        raise ValueError(
            f"{quantity} mode index {source_index} is outside the harmonic mode range"
        )
    return normalized_index


def _assign_value(
    values: NDArray[np.float64],
    index: tuple[int, ...],
    value: float,
    quantity: str,
) -> None:
    """Assign a value, rejecting duplicate entries that disagree."""
    existing = values[index]
    if not np.isnan(existing) and not np.isclose(existing, value):
        raise ValueError(
            f"{quantity} has conflicting values at normalized index {index}: "
            f"{existing} and {value}"
        )
    values[index] = value


def _normalize_harmonic_frequencies(
    raw: RawHarmonicFrequencies, source_indices: NDArray[np.int64]
) -> HarmonicFrequencies:
    """Convert contiguous CFOUR harmonic wavenumbers to a Hz mode vector."""
    values = np.array(
        [raw.by_index[int(index)] for index in source_indices], dtype=np.float64
    )
    if np.any(values <= 0.0):
        raise ValueError("CFOUR harmonic frequencies must be positive")
    return HarmonicFrequencies(values=values * WAVENUMBER_TO_HZ)


def _normalize_zetas(
    raw: RawCFOURZetas, first_mode_index: int, n_modes: int
) -> CoriolisZetas:
    """Expand CFOUR lower-triangular zeta sections to a dense core tensor."""
    values = np.full((n_modes, n_modes, 3), np.nan, dtype=np.float64)
    required_pairs = {(row, column) for row in range(n_modes) for column in range(row)}

    for axis, section in enumerate((raw.axis1, raw.axis2, raw.axis3)):
        _normalize_zeta_section(
            section, values, axis, first_mode_index, n_modes, required_pairs
        )

    return CoriolisZetas(values=np.nan_to_num(values, nan=0.0))


def _normalize_zeta_section(
    raw: RawZetasSection,
    values: NDArray[np.float64],
    axis: int,
    first_mode_index: int,
    n_modes: int,
    required_pairs: set[tuple[int, int]],
) -> None:
    """Populate one zeta rotational-axis slice and require all mode pairs."""
    if raw.mode_indices.shape != (len(raw.values), 2):
        raise ValueError("CFOUR zeta indices must have shape (n_entries, 2)")

    seen_pairs: set[tuple[int, int]] = set()
    for source_indices, value in zip(raw.mode_indices, raw.values, strict=True):
        source_row, source_column = (int(index) for index in source_indices)
        if source_row < first_mode_index or source_column < first_mode_index:
            continue
        row = _normalized_mode_index(
            source_row, first_mode_index, n_modes, "CFOUR zeta"
        )
        column = _normalized_mode_index(
            source_column, first_mode_index, n_modes, "CFOUR zeta"
        )
        if row == column:
            raise ValueError("CFOUR zeta entries must not have equal mode indices")
        pair = (max(row, column), min(row, column))
        _assign_value(values, (row, column, axis), float(value), "CFOUR zeta")
        _assign_value(values, (column, row, axis), -float(value), "CFOUR zeta")
        seen_pairs.add(pair)

    missing_pairs = required_pairs - seen_pairs
    if missing_pairs:
        raise ValueError(
            f"CFOUR zeta axis {axis + 1} is missing vibrational mode pairs: "
            f"{sorted(missing_pairs)}"
        )


def _normalize_cubic_force_constants(
    raw: RawCFOURCubic, first_mode_index: int, n_modes: int
) -> CubicForceConstants:
    """Convert and expand permutation-unique CFOUR cubic force constants."""
    if raw.mode_indices.shape != (len(raw.values), 3):
        raise ValueError("CFOUR cubic indices must have shape (n_entries, 3)")

    values = np.full((n_modes, n_modes, n_modes), np.nan, dtype=np.float64)
    for source_indices, raw_value in zip(raw.mode_indices, raw.values, strict=True):
        indices = tuple(
            _normalized_mode_index(
                int(source_index), first_mode_index, n_modes, "CFOUR cubic"
            )
            for source_index in source_indices
        )
        value = float(raw_value) * WAVENUMBER_TO_HZ
        for permutation in set(itertools.permutations(indices)):
            _assign_value(values, permutation, value, "CFOUR cubic")

    # CFOUR omits symmetry-forbidden cubic terms; their canonical value is zero.
    return CubicForceConstants(values=np.nan_to_num(values, nan=0.0))


def _normalize_inertial_derivatives(
    raw: RawCFOURdidQ, first_mode_index: int, n_modes: int
) -> InertialDerivatives:
    """Convert CFOUR didQ entries to a mode-by-axis-by-axis SI tensor."""
    if raw.mode_indices.shape != (len(raw.values), 3):
        raise ValueError("CFOUR didQ indices must have shape (n_entries, 3)")

    values = np.full((n_modes, 3, 3), np.nan, dtype=np.float64)
    for source_indices, raw_value in zip(raw.mode_indices, raw.values, strict=True):
        source_axis1, source_axis2, source_mode = (
            int(index) for index in source_indices
        )
        if not 1 <= source_axis1 <= 3 or not 1 <= source_axis2 <= 3:
            raise ValueError(
                "CFOUR didQ Cartesian indices must be between 1 and 3, "
                f"got ({source_axis1}, {source_axis2})"
            )
        mode = _normalized_mode_index(
            source_mode, first_mode_index, n_modes, "CFOUR didQ"
        )
        _assign_value(
            values,
            (mode, source_axis1 - 1, source_axis2 - 1),
            float(raw_value) * INERTIAL_DERIVATIVE_TO_SI,
            "CFOUR didQ",
        )

    if np.isnan(values).any():
        missing_indices = np.argwhere(np.isnan(values)).tolist()
        raise ValueError(f"CFOUR didQ is missing entries: {missing_indices}")
    return InertialDerivatives(values=values)


def _normalize_rotational_derivatives(
    rotational_constants: EquilibriumRotationalConstants,
    harmonic_frequencies: HarmonicFrequencies,
    inertial_derivatives: InertialDerivatives,
) -> RotationalDerivatives:
    """Calculate rotational derivatives in Hz from normalized core quantities."""
    rotational_constant_values = rotational_constants.values
    if np.any(rotational_constant_values <= 0.0):
        raise ValueError("CFOUR equilibrium rotational constants must be positive")

    equilibrium_moments = PLANCK_CONSTANT_J_S / (
        8.0 * np.pi**2 * rotational_constant_values
    )
    coefficient = -(REDUCED_PLANCK_CONSTANT_J_S**3) / (
        2.0 * PLANCK_CONSTANT_J_S ** (3.0 / 2.0)
    )
    denominator = (
        equilibrium_moments[None, :, None]
        * equilibrium_moments[None, None, :]
        * np.sqrt(harmonic_frequencies.values)[:, None, None]
    )
    return RotationalDerivatives(
        values=coefficient * inertial_derivatives.values / denominator
    )


def normalize_cfour_data(raw_data: RawDataCFOUR) -> StandardData:
    """Convert source-faithful CFOUR data into canonical core quantities."""
    logger.info("CFOUR normalization requested for '{}'.", raw_data.source_path)

    source_indices, first_mode_index = _mode_indices(
        raw_data.anharm.harmonic_frequencies
    )
    n_modes = len(source_indices)
    raw_rotational_constants = raw_data.anharm.equilibrium_rotational_constants
    rotational_constants = EquilibriumRotationalConstants(
        values=np.array(
            [
                raw_rotational_constants.X,
                raw_rotational_constants.Y,
                raw_rotational_constants.Z,
            ],
            dtype=np.float64,
        )
        * MHZ_TO_HZ
    )
    harmonic_frequencies = _normalize_harmonic_frequencies(
        raw_data.anharm.harmonic_frequencies, source_indices
    )
    coriolis_zetas = _normalize_zetas(raw_data.zetas, first_mode_index, n_modes)
    cubic_force_constants = _normalize_cubic_force_constants(
        raw_data.cubic, first_mode_index, n_modes
    )
    inertial_derivatives = _normalize_inertial_derivatives(
        raw_data.didq, first_mode_index, n_modes
    )
    rotational_derivatives = _normalize_rotational_derivatives(
        rotational_constants, harmonic_frequencies, inertial_derivatives
    )

    metadata: dict[str, object] = {
        "source_path": raw_data.source_path,
        "source_type": "CFOUR",
    }
    return StandardData(
        n_modes=n_modes,
        equilibrium_rotational_constants=rotational_constants,
        harmonic_frequencies=harmonic_frequencies,
        cubic_force_constants=cubic_force_constants,
        inertial_derivatives=inertial_derivatives,
        rotational_derivatives=rotational_derivatives,
        coriolis_zetas=coriolis_zetas,
        metadata=metadata,
    )
