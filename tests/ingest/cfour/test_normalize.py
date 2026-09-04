from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from vrvv.core.units import (
    INERTIAL_DERIVATIVE_TO_SI,
    MHZ_TO_HZ,
    PLANCK_CONSTANT_J_S,
    REDUCED_PLANCK_CONSTANT_J_S,
    WAVENUMBER_TO_HZ,
)
from vrvv.ingest.cfour.normalize import normalize_cfour_data
from vrvv.ingest.cfour.parser import CFOURParser
from vrvv.ingest.cfour.raw import RawHarmonicFrequencies, RawRotationalConstants

FIXTURE_DIR = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "cfour"


def _raw_data():
    return CFOURParser().parse_raw(FIXTURE_DIR)


def test_normalize_cfour_data_converts_fixture_to_standard_data() -> None:
    raw_data = _raw_data()

    data = normalize_cfour_data(raw_data)

    assert data.n_modes == 6
    assert data.metadata == {
        "source_path": FIXTURE_DIR,
        "source_type": "CFOUR",
        "n_atoms": 4,
        "is_linear": False,
    }
    np.testing.assert_allclose(
        data.equilibrium_rotational_constants.values,
        np.array([609196.61481899, 12111.96058742, 11875.84668995]) * MHZ_TO_HZ,
    )
    np.testing.assert_allclose(
        data.harmonic_frequencies.values,
        np.array(
            [
                raw_data.anharm.harmonic_frequencies.by_index[index]
                for index in range(7, 13)
            ]
        )
        * WAVENUMBER_TO_HZ,
    )

    assert data.coriolis_zetas.values.shape == (6, 6, 3)
    assert data.coriolis_zetas.values[1, 0, 0] == pytest.approx(-0.9518407855)
    assert data.coriolis_zetas.values[0, 1, 0] == pytest.approx(0.9518407855)
    assert data.coriolis_zetas.values[1, 0, 1] == pytest.approx(0.0680318686)

    expected_cubic = -10.5879171447 * WAVENUMBER_TO_HZ
    assert data.cubic_force_constants.values.shape == (6, 6, 6)
    assert data.cubic_force_constants.values[0, 1, 1] == pytest.approx(expected_cubic)
    assert data.cubic_force_constants.values[1, 0, 1] == pytest.approx(expected_cubic)

    expected_inertial_derivative = -1.011182136390842 * INERTIAL_DERIVATIVE_TO_SI
    assert data.inertial_derivatives.values.shape == (6, 3, 3)
    assert data.inertial_derivatives.values[0, 0, 1] == pytest.approx(
        expected_inertial_derivative
    )
    assert data.inertial_derivatives.values[0, 1, 0] == pytest.approx(
        expected_inertial_derivative
    )

    equilibrium_moments = PLANCK_CONSTANT_J_S / (
        8.0 * np.pi**2 * data.equilibrium_rotational_constants.values
    )
    coefficient = -(REDUCED_PLANCK_CONSTANT_J_S**3) / (
        2.0 * PLANCK_CONSTANT_J_S ** (3.0 / 2.0)
    )
    expected_rotational_derivative = (
        coefficient
        * expected_inertial_derivative
        / (
            equilibrium_moments[0]
            * equilibrium_moments[1]
            * np.sqrt(data.harmonic_frequencies.values[0])
        )
    )
    assert data.rotational_derivatives.values[0, 0, 1] == pytest.approx(
        expected_rotational_derivative
    )


def test_normalize_rejects_empty_harmonic_frequencies() -> None:
    raw_data = _raw_data()
    empty_harmonics = RawHarmonicFrequencies()

    with pytest.raises(ValueError, match="harmonic frequencies are empty"):
        normalize_cfour_data(
            replace(
                raw_data,
                anharm=replace(raw_data.anharm, harmonic_frequencies=empty_harmonics),
            )
        )


def test_normalize_rejects_non_contiguous_harmonic_frequencies() -> None:
    raw_data = _raw_data()
    non_contiguous_harmonics = RawHarmonicFrequencies(
        by_index={7: 531.5451, 9: 1084.1982}
    )

    with pytest.raises(ValueError, match="must be contiguous"):
        normalize_cfour_data(
            replace(
                raw_data,
                anharm=replace(
                    raw_data.anharm, harmonic_frequencies=non_contiguous_harmonics
                ),
            )
        )


def test_normalize_rejects_non_positive_harmonic_frequency() -> None:
    raw_data = _raw_data()
    harmonics = replace(
        raw_data.anharm.harmonic_frequencies,
        by_index={**raw_data.anharm.harmonic_frequencies.by_index, 7: 0.0},
    )

    with pytest.raises(ValueError, match="must be positive"):
        normalize_cfour_data(
            replace(
                raw_data,
                anharm=replace(raw_data.anharm, harmonic_frequencies=harmonics),
            )
        )


def test_normalize_rejects_non_positive_rotational_constant() -> None:
    raw_data = _raw_data()
    rotational_constants = RawRotationalConstants(
        X=0.0, Y=12111.96058742, Z=11875.84668995
    )

    with pytest.raises(ValueError, match="rotational constants must be positive"):
        normalize_cfour_data(
            replace(
                raw_data,
                anharm=replace(
                    raw_data.anharm,
                    equilibrium_rotational_constants=rotational_constants,
                ),
            )
        )


def test_normalize_rejects_missing_vibrational_zeta_pair() -> None:
    raw_data = _raw_data()
    missing_last_entry = replace(
        raw_data.zetas.axis1,
        mode_indices=raw_data.zetas.axis1.mode_indices[:-1],
        values=raw_data.zetas.axis1.values[:-1],
    )

    with pytest.raises(ValueError, match="missing vibrational mode pairs"):
        normalize_cfour_data(
            replace(raw_data, zetas=replace(raw_data.zetas, axis1=missing_last_entry))
        )


def test_normalize_rejects_cubic_mode_outside_harmonic_range() -> None:
    raw_data = _raw_data()
    cubic = replace(
        raw_data.cubic,
        mode_indices=np.vstack((raw_data.cubic.mode_indices, [13, 7, 7])),
        values=np.append(raw_data.cubic.values, 1.0),
    )

    with pytest.raises(ValueError, match="cubic mode index 13"):
        normalize_cfour_data(replace(raw_data, cubic=cubic))


def test_normalize_rejects_conflicting_cubic_entries() -> None:
    raw_data = _raw_data()
    cubic = replace(
        raw_data.cubic,
        mode_indices=np.vstack((raw_data.cubic.mode_indices, [7, 7, 7])),
        values=np.append(raw_data.cubic.values, 1.0),
    )

    with pytest.raises(ValueError, match="conflicting values"):
        normalize_cfour_data(replace(raw_data, cubic=cubic))


def test_normalize_rejects_missing_didq_entry() -> None:
    raw_data = _raw_data()
    didq = replace(
        raw_data.didq,
        mode_indices=raw_data.didq.mode_indices[:-1],
        values=raw_data.didq.values[:-1],
    )

    with pytest.raises(ValueError, match="didQ is missing entries"):
        normalize_cfour_data(replace(raw_data, didq=didq))


def test_normalize_rejects_invalid_didq_cartesian_index() -> None:
    raw_data = _raw_data()
    didq = replace(
        raw_data.didq,
        mode_indices=np.vstack((raw_data.didq.mode_indices, [4, 1, 7])),
        values=np.append(raw_data.didq.values, 1.0),
    )

    with pytest.raises(ValueError, match="Cartesian indices must be between 1 and 3"):
        normalize_cfour_data(replace(raw_data, didq=didq))
