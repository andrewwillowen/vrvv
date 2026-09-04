import numpy as np
import pytest

from vrvv.core.units import (
    ATOMIC_MASS_CONSTANT_KG,
    BOHR_RADIUS_M,
    INERTIAL_DERIVATIVE_TO_SI,
    MHZ_TO_HZ,
    PLANCK_CONSTANT_J_S,
    REDUCED_PLANCK_CONSTANT_J_S,
    SPEED_OF_LIGHT_M_PER_S,
    WAVENUMBER_TO_HZ,
)


def test_unit_constants_match_scipy_definitions() -> None:
    assert SPEED_OF_LIGHT_M_PER_S == 299_792_458.0
    assert PLANCK_CONSTANT_J_S == 6.626_070_15e-34
    assert REDUCED_PLANCK_CONSTANT_J_S == pytest.approx(
        PLANCK_CONSTANT_J_S / (2.0 * np.pi)
    )
    assert ATOMIC_MASS_CONSTANT_KG == pytest.approx(1.660_539_068_92e-27)
    assert BOHR_RADIUS_M == pytest.approx(5.291_772_105_44e-11)


def test_unit_conversion_factors_follow_their_definitions() -> None:
    assert MHZ_TO_HZ == 1_000_000.0
    assert WAVENUMBER_TO_HZ == 100.0 * SPEED_OF_LIGHT_M_PER_S
    assert INERTIAL_DERIVATIVE_TO_SI == pytest.approx(
        np.sqrt(ATOMIC_MASS_CONSTANT_KG) * BOHR_RADIUS_M
    )
