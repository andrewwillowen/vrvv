from pathlib import Path

import pytest

from vrvv.ingest.cfour.parser import CFOURParser


def test_can_parse_matches_common_suffixes() -> None:
    parser = CFOURParser()

    assert parser.can_parse(Path("job.out"))
    assert parser.can_parse(Path("job.log"))
    assert not parser.can_parse(Path("job.txt"))


def test_can_parse_matches_cfour_name_hint() -> None:
    parser = CFOURParser()

    assert parser.can_parse(Path("CFOUR-results.txt"))


def test_parse_raw_is_placeholder() -> None:
    parser = CFOURParser()

    with pytest.raises(NotImplementedError, match="not implemented yet"):
        parser.parse_raw(Path("job.out"))
