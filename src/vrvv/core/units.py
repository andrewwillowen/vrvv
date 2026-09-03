"""Physical constants and unit-conversion factors used by vrvv."""

import numpy as np
from scipy.constants import (  # type: ignore[import-untyped]
    atomic_mass,
    c,
    h,
    hbar,
    physical_constants,
)

SPEED_OF_LIGHT_M_PER_S = c
"""Speed of light in vacuum in metres per second."""

PLANCK_CONSTANT_J_S = h
"""Planck constant in joule seconds."""

REDUCED_PLANCK_CONSTANT_J_S = hbar
"""Reduced Planck constant in joule seconds."""

ATOMIC_MASS_CONSTANT_KG = atomic_mass
"""Atomic mass constant in kilograms."""

MHZ_TO_HZ = 1_000_000.0
"""Convert megahertz to hertz."""

WAVENUMBER_TO_HZ = 100.0 * c
"""Convert inverse centimetres to hertz."""

BOHR_RADIUS_M: float = physical_constants["Bohr radius"][0]
"""Bohr radius in metres."""

INERTIAL_DERIVATIVE_TO_SI = np.sqrt(ATOMIC_MASS_CONSTANT_KG) * BOHR_RADIUS_M
"""Convert sqrt(amu) * bohr to kg^(1/2) * m."""
