from pathlib import Path

import pytest

from vrvv.ingest.cfour.normalize import normalize_cfour_data
from vrvv.ingest.cfour.raw import RawDataCFOUR


def test_normalize_is_placeholder() -> None:
    raw_data = RawDataCFOUR(source_path=Path("job.out"))

    with pytest.raises(NotImplementedError, match="not implemented yet"):
        normalize_cfour_data(raw_data)
