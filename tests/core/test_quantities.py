import numpy as np
import pytest

from vrvv.core.quantities import (
    CoriolisZetas,
    CubicForceConstants,
    EquilibriumRotationalConstants,
    HarmonicFrequencies,
    InertialDerivatives,
    RotationalDerivatives,
)


def test_rotational_constants_use_axis_vector_and_named_accessors() -> None:
    constants = EquilibriumRotationalConstants(
        values=np.array([1.0, 2.0, 3.0], dtype=np.float64)
    )

    assert constants.X == 1.0
    assert constants.Y == 2.0
    assert constants.Z == 3.0


def test_rotational_constants_reject_non_axis_vector() -> None:
    with pytest.raises(ValueError, match=r"shape \(3,\)"):
        EquilibriumRotationalConstants(values=np.array([1.0, 2.0], dtype=np.float64))


def test_harmonic_frequencies_accept_mode_vector() -> None:
    frequencies = HarmonicFrequencies(
        values=np.array([1.0, 2.0, 3.0], dtype=np.float64)
    )

    assert frequencies.values.shape == (3,)


def test_harmonic_frequencies_reject_non_vector() -> None:
    with pytest.raises(ValueError, match="one-dimensional"):
        HarmonicFrequencies(values=np.zeros((2, 2), dtype=np.float64))


def test_harmonic_frequencies_reject_descending_values() -> None:
    with pytest.raises(ValueError, match="sorted lowest to highest"):
        HarmonicFrequencies(values=np.array([2.0, 1.0], dtype=np.float64))


def test_cubic_force_constants_accept_mode_tensor() -> None:
    constants = CubicForceConstants(values=np.zeros((2, 2, 2), dtype=np.float64))

    assert constants.values.shape == (2, 2, 2)


@pytest.mark.parametrize(
    ("shape", "message"),
    [
        ((2, 2), "three-dimensional"),
        ((2, 2, 3), "all three dimensions"),
    ],
)
def test_cubic_force_constants_reject_invalid_tensor_shape(
    shape: tuple[int, ...], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        CubicForceConstants(values=np.zeros(shape, dtype=np.float64))


def test_cubic_force_constants_reject_non_symmetric_values() -> None:
    values = np.zeros((2, 2, 2), dtype=np.float64)
    values[0, 1, 1] = 1.0

    with pytest.raises(ValueError, match="invariant to permutation"):
        CubicForceConstants(values=values)


@pytest.mark.parametrize(
    "derivative_type", [InertialDerivatives, RotationalDerivatives]
)
def test_derivatives_accept_mode_axis_axis_tensor(derivative_type: type) -> None:
    derivatives = derivative_type(values=np.zeros((2, 3, 3), dtype=np.float64))

    assert derivatives.values.shape == (2, 3, 3)


@pytest.mark.parametrize(
    "derivative_type", [InertialDerivatives, RotationalDerivatives]
)
@pytest.mark.parametrize("shape", [(2, 3), (2, 2, 3), (2, 3, 2)])
def test_derivatives_reject_invalid_tensor_shape(
    derivative_type: type, shape: tuple[int, ...]
) -> None:
    with pytest.raises(ValueError, match=r"shape \(n_modes, 3, 3\)"):
        derivative_type(values=np.zeros(shape, dtype=np.float64))


@pytest.mark.parametrize(
    "derivative_type", [InertialDerivatives, RotationalDerivatives]
)
def test_derivatives_reject_non_symmetric_rotational_axes(
    derivative_type: type,
) -> None:
    values = np.zeros((1, 3, 3), dtype=np.float64)
    values[0, 0, 1] = 1.0

    with pytest.raises(ValueError, match="symmetric"):
        derivative_type(values=values)


def test_coriolis_zetas_use_mode_mode_axis_tensor_and_named_accessors() -> None:
    values = np.zeros((2, 2, 3), dtype=np.float64)
    values[1, 0] = (1.0, 2.0, 3.0)
    values[0, 1] = (-1.0, -2.0, -3.0)

    zetas = CoriolisZetas(values=values)

    np.testing.assert_array_equal(zetas.X, values[:, :, 0])
    np.testing.assert_array_equal(zetas.Y, values[:, :, 1])
    np.testing.assert_array_equal(zetas.Z, values[:, :, 2])


def test_coriolis_zetas_reject_invalid_tensor_shape() -> None:
    with pytest.raises(ValueError, match=r"shape \(n_modes, n_modes, 3\)"):
        CoriolisZetas(values=np.zeros((2, 2, 2), dtype=np.float64))


def test_coriolis_zetas_reject_unequal_vibrational_dimensions() -> None:
    with pytest.raises(ValueError, match="vibrational dimensions"):
        CoriolisZetas(values=np.zeros((2, 3, 3), dtype=np.float64))


def test_coriolis_zetas_reject_non_antisymmetric_modes() -> None:
    values = np.zeros((2, 2, 3), dtype=np.float64)
    values[0, 1, 0] = 1.0

    with pytest.raises(ValueError, match="antisymmetric"):
        CoriolisZetas(values=values)
