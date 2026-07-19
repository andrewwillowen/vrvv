"""Internal text parsing helpers for CFOUR ingest."""

from collections.abc import Iterator


class CFOURTextParseError(ValueError):
    """Raised when CFOUR text parsing helpers cannot parse expected input."""


def extract_section(text: str, start_marker: str, end_marker: str) -> str:
    """Extract the text between start and end markers."""
    start_index = text.find(start_marker)
    if start_index < 0:
        message = f"Missing section start marker: {start_marker!r}"
        raise CFOURTextParseError(message)

    content_start = start_index + len(start_marker)
    end_index = text.find(end_marker, content_start)
    if end_index < 0:
        message = f"Missing section end marker: {end_marker!r} (after start marker {start_marker!r})"
        raise CFOURTextParseError(message)

    return text[content_start:end_index]


def iter_data_lines(
    section_text: str,
    *,
    skip_blank: bool = True,
    skip_dash_lines: bool = True,
    skip_prefixes: tuple[str, ...] = (),
) -> Iterator[str]:
    """Yield normalized data lines from a text section."""
    for raw_line in section_text.splitlines():
        line = raw_line.strip()

        if skip_blank and not line:
            continue

        if skip_dash_lines and set(line) == {"-"}:
            continue

        if any(line.startswith(prefix) for prefix in skip_prefixes):
            continue

        yield line


def parse_labeled_float_row(line: str, *, n_values: int) -> tuple[str, tuple[float, ...]]:
    """Parse ``<label> <float> <float> ...`` rows."""
    parts = line.split()
    expected_columns = n_values + 1
    if len(parts) != expected_columns:
        message = f"Expected {expected_columns} columns in labeled row, got {len(parts)}: {line!r}"
        raise CFOURTextParseError(message)

    label = parts[0]
    try:
        values = tuple(float(token) for token in parts[1:])
    except ValueError as error:
        message = f"Invalid float token in labeled row: {line!r}"
        raise CFOURTextParseError(message) from error

    return label, values


def parse_indexed_value_row(
    line: str,
    *,
    n_indices: int,
    one_indexed: bool = True,
) -> tuple[tuple[int, ...], float]:
    """Parse ``<index> <index> ... <value>`` rows."""
    parts = line.split()
    expected_columns = n_indices + 1
    if len(parts) != expected_columns:
        message = f"Expected {expected_columns} columns in indexed row, got {len(parts)}: {line!r}"
        raise CFOURTextParseError(message)

    raw_indices = parts[:n_indices]
    raw_value = parts[-1]

    try:
        indices = tuple(int(token) for token in raw_indices)
    except ValueError as error:
        message = f"Invalid integer token in indexed row: {line!r}"
        raise CFOURTextParseError(message) from error

    if one_indexed:
        if any(index <= 0 for index in indices):
            message = f"One-indexed row contains non-positive index: {line!r}"
            raise CFOURTextParseError(message)
        indices = tuple(index - 1 for index in indices)

    try:
        value = float(raw_value)
    except ValueError as error:
        message = f"Invalid float value in indexed row: {line!r}"
        raise CFOURTextParseError(message) from error

    return indices, value
