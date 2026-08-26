from pathlib import Path

import numpy as np
import pytest

from vrvv.ingest.cfour.normalize import normalize_cfour_data
from vrvv.ingest.cfour.raw import (
    RawCFOURAnharm,
    RawCFOURCubic,
    RawCFOURdidQ,
    RawCFOURZetas,
    RawDataCFOUR,
    RawHarmonicFrequencies,
    RawRotationalConstants,
    RawZetasSection,
)


def _empty_zetas_section() -> RawZetasSection:
    return RawZetasSection(
        mode_indices=np.empty((0, 2), dtype=np.int64),
        values=np.empty(0, dtype=np.float64),
    )


def test_normalize_is_placeholder() -> None:
    raw_data = RawDataCFOUR(
        source_path=Path("job.out"),
        anharm=RawCFOURAnharm(
            equilibrium_rotational_constants=RawRotationalConstants(X=0, Y=0, Z=0),
            harmonic_frequencies=RawHarmonicFrequencies(),
        ),
        zetas=RawCFOURZetas(
            axis1=_empty_zetas_section(),
            axis2=_empty_zetas_section(),
            axis3=_empty_zetas_section(),
        ),
        cubic=RawCFOURCubic(
            mode_indices=np.empty((0, 3), dtype=np.int64),
            values=np.empty(0, dtype=np.float64),
        ),
        didq=RawCFOURdidQ(
            mode_indices=np.empty((0, 3), dtype=np.int64),
            values=np.empty(0, dtype=np.float64),
        ),
    )

    with pytest.raises(NotImplementedError, match="not implemented yet"):
        normalize_cfour_data(raw_data)
