import csv
from pathlib import Path

from vrvv.core.export import export_standard_data
from vrvv.ingest.cfour.normalize import normalize_cfour_data
from vrvv.ingest.cfour.parser import CFOURParser

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "cfour"


def test_export_standard_data_writes_component_csv_files(tmp_path) -> None:
    data = normalize_cfour_data(CFOURParser().parse_raw(FIXTURE_DIR))

    paths = export_standard_data(data, tmp_path / "csv")

    assert {path.name for path in paths} == {
        "equilibrium_rotational_constants.csv",
        "harmonic_frequencies.csv",
        "cubic_force_constants.csv",
        "inertial_derivatives.csv",
        "rotational_derivatives.csv",
        "coriolis_zetas.csv",
        "metadata.csv",
    }
    with (tmp_path / "csv" / "harmonic_frequencies.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        rows = list(csv.reader(stream))
    assert rows[0] == ["mode_index_zero_based", "frequency_hz"]
    assert rows[1][0] == "0"
    assert len(rows) == data.n_modes + 1
