from pathlib import Path

import pytest

from vrvv.ingest.cfour.parser import CFOURParser


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
