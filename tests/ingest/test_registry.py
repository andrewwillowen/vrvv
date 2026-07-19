from pathlib import Path

import pytest

from vrvv.ingest import registry
from vrvv.ingest.base import (
    ParserAutodetectError,
    ParserNotFoundError,
    ParserRegistryError,
)


class DummyParser:
    def __init__(self, name: str, match_mode: str) -> None:
        self.name = name
        self._match_mode = match_mode

    def can_parse(self, _path: Path) -> bool:
        return self._match_mode == "match"

    def parse_raw(self, path: Path) -> object:
        return {"path": str(path)}


@pytest.fixture(autouse=True)
def reset_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(registry, "_PARSERS", {})


def test_register_and_get_parser() -> None:
    parser = DummyParser("dummy", match_mode="match")
    registry.register_parser(parser)

    assert registry.get_parser("dummy") is parser


def test_duplicate_registration_raises_error() -> None:
    parser = DummyParser("dummy", match_mode="match")
    registry.register_parser(parser)

    with pytest.raises(ParserRegistryError, match="already registered"):
        registry.register_parser(DummyParser("dummy", match_mode="skip"))


def test_get_unknown_parser_raises_error() -> None:
    with pytest.raises(ParserNotFoundError, match="Unknown parser"):
        registry.get_parser("missing")


def test_autodetect_returns_only_match() -> None:
    expected = DummyParser("only", match_mode="match")
    registry.register_parser(DummyParser("skip", match_mode="skip"))
    registry.register_parser(expected)

    assert registry.autodetect_parser(Path("sample.out")) is expected


def test_autodetect_raises_for_no_matches() -> None:
    registry.register_parser(DummyParser("skip", match_mode="skip"))

    with pytest.raises(ParserAutodetectError, match="No parser matched"):
        registry.autodetect_parser(Path("sample.out"))


def test_autodetect_raises_for_ambiguous_matches() -> None:
    registry.register_parser(DummyParser("a", match_mode="match"))
    registry.register_parser(DummyParser("b", match_mode="match"))

    with pytest.raises(ParserAutodetectError, match="Ambiguous parser autodetect"):
        registry.autodetect_parser(Path("sample.out"))


def test_load_builtin_parsers_registers_cfour() -> None:
    registry.load_builtin_parsers()

    assert "cfour" in registry.list_parsers()
