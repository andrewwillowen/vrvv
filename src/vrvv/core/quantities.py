"""
Base units and conversions of physical quantities.
"""

import itertools
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


@dataclass(slots=True)
class StandardData:
    """Canonical collection of normalized input quantities."""

    n_modes: int
    equilibrium_rotational_constants: "EquilibriumRotationalConstants"
    harmonic_frequencies: "HarmonicFrequencies"
    cubic_force_constants: "CubicForceConstants"
    inertial_derivatives: "InertialDerivatives"
    rotational_derivatives: "RotationalDerivatives"
    coriolis_zetas: "CoriolisZetas"
    metadata: dict[str, object] = field(default_factory=dict)

    def to_csv(self, output_dir: Path) -> list[Path]:
        """Export all components to CSV files in ``output_dir``."""
        from vrvv.core.export import export_standard_data

        return export_standard_data(self, output_dir)

    def to_dat(self, output_path: Path) -> Path:
        """Export normalized data to the legacy fixed-width DAT format."""
        from vrvv.core.export import export_standard_data_dat

        return export_standard_data_dat(self, output_path)

    def __post_init__(self) -> None:
        """Ensure every vibrationally indexed quantity has n_modes entries."""
        if self.n_modes < 0:
            raise ValueError(f"n_modes must be non-negative, got {self.n_modes}")

        # Each quantity validates its own tensor shape. Its leading axis is
        # therefore sufficient to establish the shared vibrational mode count:
        # cubic and zeta tensors validate their remaining mode axes, while
        # derivative tensors validate their trailing Cartesian axes.
        mode_counts = {
            "harmonic_frequencies": self.harmonic_frequencies.values.shape[0],
            "cubic_force_constants": self.cubic_force_constants.values.shape[0],
            "inertial_derivatives": self.inertial_derivatives.values.shape[0],
            "rotational_derivatives": self.rotational_derivatives.values.shape[0],
            "coriolis_zetas": self.coriolis_zetas.values.shape[0],
        }
        mismatches = {
            name: count for name, count in mode_counts.items() if count != self.n_modes
        }
        if mismatches:
            raise ValueError(
                f"mode-indexed quantities must have n_modes={self.n_modes}, "
                f"got {mismatches}"
            )


@dataclass(slots=True)
class EquilibriumRotationalConstants:
    """Equilibrium rotational constants B[alpha] in Hz."""

    values: NDArray[np.float64]

    def __post_init__(self) -> None:
        """Ensure the rotational-axis vector has exactly three components."""
        if self.values.shape != (3,):
            raise ValueError(
                f"values must have shape (3,) for X, Y, Z, got {self.values.shape}"
            )

    @property
    def X(self) -> np.float64:
        """Equilibrium rotational constant for the X axis."""
        return self.values[0]

    @property
    def Y(self) -> np.float64:
        """Equilibrium rotational constant for the Y axis."""
        return self.values[1]

    @property
    def Z(self) -> np.float64:
        """Equilibrium rotational constant for the Z axis."""
        return self.values[2]


@dataclass(slots=True)
class HarmonicFrequencies:
    """Harmonic vibrational frequencies nu[k] in Hz."""

    values: NDArray[np.float64]

    def __post_init__(self) -> None:
        """Make sure that the "array" is a vector, sorted ascending"""
        if self.values.ndim != 1:
            raise ValueError(
                f"values must be one-dimensional, got shape {self.values.shape}"
            )
        if not np.all(np.diff(self.values) >= 0):
            raise ValueError(
                f"values must be sorted lowest to highest, got {self.values}"
            )


@dataclass(slots=True)
class CubicForceConstants:
    """Cubic force constants k[i, j, k] in Hz."""

    values: NDArray[np.float64]

    def __post_init__(self) -> None:
        """Make sure that the arrays are three-dimensional and square."""
        shapes = self.values.shape
        if len(shapes) != 3:
            raise ValueError(f"values must be three-dimensional, not {shapes}")
        if len(set(shapes)) != 1:
            raise ValueError(
                f"all three dimensions must have the same length, got {shapes}"
            )
        for perm in itertools.permutations((0, 1, 2)):
            if not np.allclose(self.values, self.values.transpose(perm)):
                raise ValueError(
                    "values must be invariant to permutation of indices, "
                    f"failed for permutation {perm}"
                )


@dataclass(slots=True)
class InertialDerivatives:
    """Inertial derivatives a[k, alpha, beta] in kg^(1/2) * m."""

    values: NDArray[np.float64]

    def __post_init__(self) -> None:
        """Make sure the values are symmetric with respect to the rotational indices."""
        if self.values.ndim != 3 or self.values.shape[1:] != (3, 3):
            raise ValueError(
                f"values must have shape (n_modes, 3, 3), got {self.values.shape}"
            )
        if not np.allclose(self.values, self.values.transpose(0, 2, 1)):
            raise ValueError(
                "values must be symmetric in the rotational axis dimensions"
            )


@dataclass(slots=True)
class RotationalDerivatives:
    """Rotational derivatives B[k, alpha, beta] in Hz."""

    values: NDArray[np.float64]

    def __post_init__(self) -> None:
        """Make sure the values are symmetric with respect to the rotational indices."""
        if self.values.ndim != 3 or self.values.shape[1:] != (3, 3):
            raise ValueError(
                f"values must have shape (n_modes, 3, 3), got {self.values.shape}"
            )
        if not np.allclose(self.values, self.values.transpose(0, 2, 1)):
            raise ValueError(
                "values must be symmetric in the rotational axis dimensions"
            )


@dataclass(slots=True)
class CoriolisZetas:
    """Dimensionless Coriolis zeta[i, j, alpha] coupling constants."""

    values: NDArray[np.float64]

    def __post_init__(self) -> None:
        """Ensure square vibrational axes and antisymmetry for every rotation axis."""
        if self.values.ndim != 3 or self.values.shape[2] != 3:
            raise ValueError(
                f"values must have shape (n_modes, n_modes, 3), got {self.values.shape}"
            )
        if self.values.shape[0] != self.values.shape[1]:
            raise ValueError(
                "the vibrational dimensions must have equal length, "
                f"got {self.values.shape}"
            )
        if not np.allclose(self.values, -self.values.transpose(1, 0, 2)):
            raise ValueError(
                "values must be antisymmetric in the vibrational mode dimensions"
            )

    @property
    def X(self) -> NDArray[np.float64]:
        """Coriolis zeta matrix for the X rotational axis."""
        return self.values[:, :, 0]

    @property
    def Y(self) -> NDArray[np.float64]:
        """Coriolis zeta matrix for the Y rotational axis."""
        return self.values[:, :, 1]

    @property
    def Z(self) -> NDArray[np.float64]:
        """Coriolis zeta matrix for the Z rotational axis."""
        return self.values[:, :, 2]
