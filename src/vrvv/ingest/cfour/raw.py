"""Typed dataclasses for holding CFOUR-specific raw data."""

import dataclasses as dc
from pathlib import Path


@dc.dataclass(slots=True)
class HarmonicFrequencies:
    values_cm1: list[float] = dc.field(default_factory=list)


@dc.dataclass(slots=True)
class RawDataCFOUR:
    source_path: Path
    harmonic_frequencies: HarmonicFrequencies = dc.field(default_factory=HarmonicFrequencies)


@dc.dataclass(slots=True)
class RawCFOURAnharm:
    pass


@dc.dataclass(slots=True)
class RawCFOURCubic:
    pass


@dc.dataclass(slots=True)
class RawCFOURdidQ:
    pass


@dc.dataclass(slots=True)
class RawCFOURZetas:
    pass
