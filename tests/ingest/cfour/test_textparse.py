import pytest

from vrvv.ingest.cfour._textparse import (
    CFOURTextParseError,
    extract_section,
    iter_data_lines,
    parse_indexed_value_row,
    parse_labeled_float_row,
)


def test_extract_section_returns_text_between_markers() -> None:
    text = "header\nSTART\nline-1\nline-2\nEND\nfooter\n"

    result = extract_section(text, "START", "END")

    assert result == "\nline-1\nline-2\n"


def test_extract_section_raises_when_start_marker_missing() -> None:
    with pytest.raises(CFOURTextParseError, match="Missing section start marker"):
        extract_section("abc", "START", "END")


def test_extract_section_raises_when_end_marker_missing() -> None:
    with pytest.raises(CFOURTextParseError, match="Missing section end marker"):
        extract_section("START only", "START", "END")


def test_iter_data_lines_filters_blanks_separators_and_prefixes() -> None:
    section = "\n  VIBRATION X Y Z\n  -----------\n  Be 1.0 2.0 3.0\n   \n  B0 4.0 5.0 6.0\n"

    rows = list(iter_data_lines(section, skip_prefixes=("VIBRATION",)))

    assert rows == ["Be 1.0 2.0 3.0", "B0 4.0 5.0 6.0"]


def test_parse_labeled_float_row_parses_expected_columns() -> None:
    label, values = parse_labeled_float_row("Be 1.0 2.0 3.0", n_values=3)

    assert label == "Be"
    assert values == (1.0, 2.0, 3.0)


def test_parse_labeled_float_row_raises_on_bad_column_count() -> None:
    with pytest.raises(CFOURTextParseError, match="Expected 4 columns"):
        parse_labeled_float_row("Be 1.0 2.0", n_values=3)


def test_parse_indexed_value_row_parses_one_indexed_indices() -> None:
    indices, value = parse_indexed_value_row("2 4 -0.125", n_indices=2)

    assert indices == (1, 3)
    assert value == -0.125


def test_parse_indexed_value_row_supports_zero_indexed_input() -> None:
    indices, value = parse_indexed_value_row("0 3 10.5", n_indices=2, one_indexed=False)

    assert indices == (0, 3)
    assert value == 10.5


def test_parse_indexed_value_row_raises_for_non_positive_one_indexed() -> None:
    with pytest.raises(CFOURTextParseError, match="non-positive index"):
        parse_indexed_value_row("0 1 1.0", n_indices=2)
