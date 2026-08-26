from pathlib import Path

import pytest

from vrvv.ingest.cfour.parser import (
    CFOURParser,
    parse_anharm_out,
    parse_harmonic_frequencies,
    parse_rotational_constants,
    parse_zetas,
)

FIXTURE_ANHARM_OUT = (
    Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "cfour" / "anharm.out"
)
FIXTURE_CORIOLIS_ZETA = (
    Path(__file__).resolve().parents[3]
    / "tests"
    / "fixtures"
    / "cfour"
    / "corioliszeta"
)


def test_can_parse_requires_all_expected_files_in_strict_mode(tmp_path) -> None:
    parser = CFOURParser()
    for name in ("anharm.out", "corioliszeta", "cubic", "didQ"):
        (tmp_path / name).write_text("")

    assert parser.can_parse(tmp_path, strict=True)


def test_can_parse_allows_partial_set_in_non_strict_mode(tmp_path) -> None:
    parser = CFOURParser()
    (tmp_path / "anharm.out").write_text("")

    assert not parser.can_parse(tmp_path, strict=True)
    assert parser.can_parse(tmp_path, strict=False)


def test_can_parse_rejects_non_directory_input(tmp_path) -> None:
    parser = CFOURParser()
    path = tmp_path / "anharm.out"
    path.write_text("")

    assert not parser.can_parse(path, strict=True)
    assert not parser.can_parse(path, strict=False)


def test_parse_raw_is_placeholder() -> None:
    parser = CFOURParser()

    with pytest.raises(NotImplementedError, match="not implemented yet"):
        parser.parse_raw(Path("cfour-run"))


def test_parse_rotational_constants_from_fixture() -> None:
    text = FIXTURE_ANHARM_OUT.read_text()

    constants = parse_rotational_constants(text)

    assert constants.X == pytest.approx(609196.61481899)
    assert constants.Y == pytest.approx(12111.96058742)
    assert constants.Z == pytest.approx(11875.84668995)


def test_parse_harmonic_frequencies_from_fixture_keeps_cfour_mode_indices() -> None:
    text = FIXTURE_ANHARM_OUT.read_text()

    frequencies = parse_harmonic_frequencies(text)

    assert frequencies.first_mode_index == 7
    assert set(frequencies.by_index) == {7, 8, 9, 10, 11, 12}
    assert frequencies.by_index[7] == pytest.approx(531.5451)
    assert frequencies.by_index[12] == pytest.approx(3521.9515)


def test_parse_anharm_out_builds_raw_dataclass_from_fixture() -> None:
    raw = parse_anharm_out(FIXTURE_ANHARM_OUT)

    assert raw.equilibrium_rotational_constants.X == pytest.approx(609196.61481899)
    assert raw.harmonic_frequencies.by_index[7] == pytest.approx(531.5451)


def test_parse_zetas_preserves_cfour_lower_triangular_entries() -> None:
    raw = parse_zetas(FIXTURE_CORIOLIS_ZETA)

    for section in (raw.axis1, raw.axis2, raw.axis3):
        assert section.mode_indices.shape == (66, 2)
        assert section.values.shape == (66,)

    assert tuple(raw.axis1.mode_indices[27]) == (8, 7)
    assert raw.axis1.values[27] == pytest.approx(-0.9518407855)
    assert tuple(raw.axis2.mode_indices[27]) == (8, 7)
    assert raw.axis2.values[27] == pytest.approx(0.0680318686)
    assert tuple(raw.axis3.mode_indices[-1]) == (12, 11)
    assert raw.axis3.values[-1] == pytest.approx(0.0839831602)
