"""
Base units and conversions of physical quantities.
"""

import itertools
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray


@dataclass(slots=True)
class StandardData:
    """Canonical placeholder container for normalized ingest outputs."""

    metadata: dict[str, object] = field(default_factory=dict)


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
