from pathlib import Path

import pytest

from vrvv.ingest.cfour._textparse import CFOURTextParseError
from vrvv.ingest.cfour.parser import (
    CFOURParser,
    parse_anharm_out,
    parse_cubic,
    parse_harmonic_frequencies,
    parse_rotational_constants,
    parse_zetas,
    parse_zetas_by_section,
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
FIXTURE_CUBIC = (
    Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "cfour" / "cubic"
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

    assert pytest.approx(609196.61481899) == constants.X
    assert pytest.approx(12111.96058742) == constants.Y
    assert pytest.approx(11875.84668995) == constants.Z


def test_parse_harmonic_frequencies_from_fixture_keeps_cfour_mode_indices() -> None:
    text = FIXTURE_ANHARM_OUT.read_text()

    frequencies = parse_harmonic_frequencies(text)

    assert frequencies.first_mode_index == 7
    assert set(frequencies.by_index) == {7, 8, 9, 10, 11, 12}
    assert frequencies.by_index[7] == pytest.approx(531.5451)
    assert frequencies.by_index[12] == pytest.approx(3521.9515)


def test_parse_anharm_out_builds_raw_dataclass_from_fixture() -> None:
    raw = parse_anharm_out(FIXTURE_ANHARM_OUT)

    assert pytest.approx(609196.61481899) == raw.equilibrium_rotational_constants.X
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


def test_parse_zetas_raises_on_empty_section() -> None:
    with pytest.raises(ValueError, match="empty"):
        parse_zetas_by_section("")


def test_parse_zetas_raises_on_blank_only_section() -> None:
    with pytest.raises(ValueError, match="empty"):
        parse_zetas_by_section("\n\n   \n")


def test_parse_zetas_raises_on_wrong_column_count() -> None:
    with pytest.raises(CFOURTextParseError, match="Expected 3 columns"):
        parse_zetas_by_section("7    7\n")


def test_parse_zetas_raises_on_invalid_index_token() -> None:
    with pytest.raises(CFOURTextParseError, match="Invalid integer token"):
        parse_zetas_by_section("7    x    -0.9518407855\n")


def test_parse_zetas_raises_on_invalid_value_token() -> None:
    with pytest.raises(CFOURTextParseError, match="Invalid float value"):
        parse_zetas_by_section("7    7    not-a-float\n")


def test_parse_zetas_raises_on_missing_axis1_start_marker(tmp_path) -> None:
    text = FIXTURE_CORIOLIS_ZETA.read_text()
    axis1_marker = "Coriolis Zeta matrix for IXYZ=                     1 :"
    text_missing_axis1_marker = text.replace(axis1_marker, "", 1)
    missing_marker_zeta = tmp_path / "corioliszeta"
    missing_marker_zeta.write_text(text_missing_axis1_marker)

    with pytest.raises(CFOURTextParseError, match="Missing section start marker"):
        parse_zetas(missing_marker_zeta)


def test_parse_zetas_raises_on_missing_axis2_end_marker(tmp_path) -> None:
    text = FIXTURE_CORIOLIS_ZETA.read_text()
    axis2_marker = "Coriolis Zeta matrix for IXYZ=                     2 :"
    truncated = text[: text.index(axis2_marker)]
    truncated_zeta = tmp_path / "corioliszeta"
    truncated_zeta.write_text(truncated)

    with pytest.raises(CFOURTextParseError, match="Missing section end marker"):
        parse_zetas(truncated_zeta)


def test_parse_cubic_preserves_cfour_permutation_unique_entries() -> None:
    raw = parse_cubic(FIXTURE_CUBIC)

    assert raw.mode_indices.shape == (40, 3)
    assert raw.values.shape == (40,)
    assert tuple(raw.mode_indices[0]) == (7, 7, 7)
    assert raw.values[0] == pytest.approx(-18.0473876585)
    assert tuple(raw.mode_indices[-1]) == (12, 12, 12)
    assert raw.values[-1] == pytest.approx(2312.2632715621)


def test_parse_cubic_raises_on_empty_file(tmp_path) -> None:
    empty_cubic = tmp_path / "cubic"
    empty_cubic.write_text("")

    with pytest.raises(ValueError, match="empty"):
        parse_cubic(empty_cubic)


def test_parse_cubic_raises_on_blank_only_file(tmp_path) -> None:
    blank_cubic = tmp_path / "cubic"
    blank_cubic.write_text("\n\n   \n")

    with pytest.raises(ValueError, match="empty"):
        parse_cubic(blank_cubic)


def test_parse_cubic_raises_on_wrong_column_count(tmp_path) -> None:
    malformed_cubic = tmp_path / "cubic"
    malformed_cubic.write_text("7    7    7\n")

    with pytest.raises(CFOURTextParseError, match="Expected 4 columns"):
        parse_cubic(malformed_cubic)


def test_parse_cubic_raises_on_invalid_index_token(tmp_path) -> None:
    malformed_cubic = tmp_path / "cubic"
    malformed_cubic.write_text("7    x    7    -18.0473876585\n")

    with pytest.raises(CFOURTextParseError, match="Invalid integer token"):
        parse_cubic(malformed_cubic)


def test_parse_cubic_raises_on_invalid_value_token(tmp_path) -> None:
    malformed_cubic = tmp_path / "cubic"
    malformed_cubic.write_text("7    7    7    not-a-float\n")

    with pytest.raises(CFOURTextParseError, match="Invalid float value"):
        parse_cubic(malformed_cubic)
