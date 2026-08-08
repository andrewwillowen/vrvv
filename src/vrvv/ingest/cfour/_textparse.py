"""Internal text parsing helpers for CFOUR ingest."""

from collections.abc import Iterator


class CFOURTextParseError(ValueError):
    """Raised when CFOUR text parsing helpers cannot parse expected input."""


def extract_section(text: str, start_marker: str, end_marker: str) -> str:
    """Extract the text between start and end markers.
    
    Locates ``start_marker`` in the input text, then extracts everything that follows
    it (up to but not including ``end_marker``). This is useful for isolating data
    sections from CFOUR output files that are bounded by recognizable delimiters.
    
    The markers themselves are not included in the returned text.
    
    Args:
        text: The full text to search (e.g., entire contents of a CFOUR file).
        start_marker: The string that marks the beginning of the section to extract.
        end_marker: The string that marks the end of the section.
    
    Returns:
        The text content between (and excluding) the two markers.
    
    Raises:
        CFOURTextParseError: If ``start_marker`` is not found in text, or if
            ``end_marker`` is not found after the start marker.
    
    Example:
        >>> text = \"\"\"
        ... == FREQUENCIES ==
        ... 1000.5
        ... 2000.3
        ... == END ==
        ... other stuff
        ... \"\"\"
        >>> section = extract_section(text, "== FREQUENCIES ==", "== END ==")
        >>> print(section)  # doctest: +NORMALIZE_WHITESPACE
        <BLANKLINE>
        1000.5
        2000.3
        <BLANKLINE>
    """
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
    """Yield normalized data lines from a text section, filtering unwanted rows.
    
    Processes a multi-line text section line-by-line, filtering and normalizing
    each line. This is useful for removing headers, separators, and other
    non-data lines before passing to value parsers like ``parse_labeled_float_row``.
    
    Each line is stripped of leading/trailing whitespace before filtering logic
    is applied.
    
    Args:
        section_text: The text section to process (typically output of extract_section).
        skip_blank: If True, skip empty lines (default: True). Useful for ignoring
            blank lines between data rows.
        skip_dash_lines: If True, skip lines that contain only dashes, like
            "----------" (default: True). Useful for filtering separator lines.
        skip_prefixes: A tuple of strings; any line starting with any of these
            strings is skipped. Useful for filtering comments (e.g., skip_prefixes=("#", "!")
            to skip lines starting with # or !). Default: empty tuple (skip nothing).
    
    Yields:
        Stripped, normalized lines that passed all filtering criteria.
    
    Example:
        >>> section = \"\"\"
        ... -- Data Section --
        ...
        ... 1000.5
        ... # This is a comment
        ... 2000.3
        ... -----------
        ... 3000.1
        ...
        ... \"\"\"
        >>> lines = list(iter_data_lines(section, skip_prefixes=("#",)))
        >>> print(lines)
        ['-- Data Section --', '1000.5', '2000.3', '3000.1']
    
    Typical usage in a parser:
        ::
        
            section = extract_section(file_text, "== FREQUENCIES ==", "== END ==")
            for line in iter_data_lines(section, skip_prefixes=("!")):
                label, (freq,) = parse_labeled_float_row(line, n_values=1)
                frequencies.append(freq)
    """
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
    """Parse ``<label> <float> <float> ...`` rows.
    
    Extracts a label (typically a string identifier) followed by one or more
    floating-point values from a whitespace-delimited row. This is a common
    pattern in CFOUR output where frequencies or other scalar quantities are
    prefixed with a mode identifier.
    
    The line is split on whitespace, so multiple consecutive spaces are treated
    as a single delimiter. The first token becomes the label; remaining tokens
    are parsed as floats.
    
    Args:
        line: A single line to parse (typically from iter_data_lines).
        n_values: The expected number of float values after the label.
            Must match the actual number of values, or a CFOURTextParseError is raised.
    
    Returns:
        A tuple of (label, values_tuple), where label is a string and
        values_tuple is a tuple of floats with length == n_values.
    
    Raises:
        CFOURTextParseError: If the line does not contain exactly (n_values + 1)
            whitespace-separated tokens, or if any token after the label cannot
            be parsed as a float.
    
    Example:
        >>> line = "mode1 1234.567 0.5"
        >>> label, values = parse_labeled_float_row(line, n_values=2)
        >>> print(label)
        mode1
        >>> print(values)
        (1234.567, 0.5)
        
        >>> # Single value:
        >>> line = "frequency_1 1000.0"
        >>> label, (freq,) = parse_labeled_float_row(line, n_values=1)
        >>> print(f"{label}: {freq}")
        frequency_1: 1000.0
    
    Typical usage in a parser:
        ::
        
            for line in iter_data_lines(section):
                label, values = parse_labeled_float_row(line, n_values=3)
                # label might be "mode1", values might be (100.0, 0.5, -0.01)
                process_mode(label, values)
    """
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
    n_values: int = 1,
    one_indexed: bool = True,
) -> tuple[tuple[int, ...], tuple[float, ...]]:
    """Parse ``<index> <index> ... <value> <value> ...`` rows.
    
    Extracts a tuple of indices (typically dimension/mode references) followed by
    one or more floating-point values from a whitespace-delimited row. This pattern
    is common in CFOUR output for force constants and other tensors, where the
    index tuple identifies which element of the tensor is being specified, and
    multiple values may be associated with that element.
    
    By default, indices are assumed to be one-indexed (as in Fortran/CFOUR output)
    and are automatically converted to zero-indexed for Python use. This conversion
    can be disabled if the input is already zero-indexed.
    
    Args:
        line: A single line to parse (typically from iter_data_lines).
        n_indices: The expected number of indices before the values.
            Must match the actual number of index tokens, or an error is raised.
        n_values: The expected number of floating-point values after the indices
            (default: 1). Must match the actual number of value tokens, or an
            error is raised.
        one_indexed: If True (default), input indices are one-indexed (starting at 1)
            and are converted to zero-indexed (starting at 0). If False, input is
            assumed to already be zero-indexed and returned as-is.
    
    Returns:
        A tuple of (index_tuple, values_tuple), where index_tuple is a tuple of ints
        (zero-indexed if one_indexed=True) and values_tuple is a tuple of floats
        with length == n_values.
    
    Raises:
        CFOURTextParseError: If the line does not contain exactly (n_indices + n_values)
            whitespace-separated tokens, if any index token cannot be parsed as int,
            if any value token cannot be parsed as float, or (if one_indexed=True)
            if any input index is <= 0.
    
    Example - single value per index (cubic force constants, 1-indexed from file):
        >>> # CFOUR output: "1 1 1 123.456" means F_{000} = 123.456 (cubic constant)
        >>> line = "1 1 1 123.456"
        >>> indices, values = parse_indexed_value_row(line, n_indices=3, n_values=1)
        >>> print(f"indices: {indices}, values: {values}")
        indices: (0, 0, 0), values: (123.456,)
        
        >>> # Another example: "2 3 45.6"
        >>> line = "2 3 45.6"
        >>> indices, (value,) = parse_indexed_value_row(line, n_indices=2, n_values=1)
        >>> print(f"Matrix element ({indices}): {value}")
        Matrix element ((1, 2)): 45.6
    
    Example - multiple values per index:
        >>> # Quadratic force constants with both real and imaginary parts: "1 2 100.5 -0.01"
        >>> line = "1 2 100.5 -0.01"
        >>> indices, (real, imag) = parse_indexed_value_row(line, n_indices=2, n_values=2)
        >>> print(f"F[{indices}] = {real} + {imag}i")
        F[(0, 1)] = 100.5 + -0.01i
    
    Example - already zero-indexed:
        >>> # If input is already zero-indexed, disable conversion:
        >>> line = "0 0 0 100.0"
        >>> indices, (value,) = parse_indexed_value_row(line, n_indices=3, n_values=1, one_indexed=False)
        >>> print(indices)
        (0, 0, 0)
    
    Typical usage in a parser (building a sparse matrix/tensor):
        ::
        
            cubic_constants = {}
            for line in iter_data_lines(cubic_section):
                indices, (value,) = parse_indexed_value_row(line, n_indices=3, n_values=1)
                cubic_constants[indices] = value  # Sparse representation
            
            # Or with multiple values per index:
            derivatives = {}
            for line in iter_data_lines(derivative_section):
                indices, values = parse_indexed_value_row(line, n_indices=2, n_values=3)
                derivatives[indices] = values  # Store all 3 derivative components
    """
    parts = line.split()
    expected_columns = n_indices + n_values
    if len(parts) != expected_columns:
        message = f"Expected {expected_columns} columns in indexed row, got {len(parts)}: {line!r}"
        raise CFOURTextParseError(message)

    raw_indices = parts[:n_indices]
    raw_values = parts[n_indices:]

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
        values = tuple(float(token) for token in raw_values)
    except ValueError as error:
        message = f"Invalid float value in indexed row: {line!r}"
        raise CFOURTextParseError(message) from error

    return indices, values
