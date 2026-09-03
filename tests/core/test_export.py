import csv
from pathlib import Path

from vrvv.core.export import export_standard_data
from vrvv.ingest.cfour.normalize import normalize_cfour_data
from vrvv.ingest.cfour.parser import CFOURParser

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "cfour"


def test_export_standard_data_writes_component_csv_files(tmp_path) -> None:
    data = normalize_cfour_data(CFOURParser().parse_raw(FIXTURE_DIR))

    paths = export_standard_data(data, tmp_path / "csv")

    expected_shapes = {
        "equilibrium_rotational_constants.csv": (
            ["rotational_axis", "value_hz"],
            3,
        ),
        "harmonic_frequencies.csv": (
            ["mode_index_zero_based", "frequency_hz"],
            data.n_modes,
        ),
        "cubic_force_constants.csv": (
            [
                "mode_i_zero_based",
                "mode_j_zero_based",
                "mode_k_zero_based",
                "value_hz",
            ],
            data.n_modes**3,
        ),
        "inertial_derivatives.csv": (
            ["mode_index_zero_based", "axis_alpha", "axis_beta", "value_kg^0.5_m"],
            data.n_modes * 3**2,
        ),
        "rotational_derivatives.csv": (
            ["mode_index_zero_based", "axis_alpha", "axis_beta", "value_hz"],
            data.n_modes * 3**2,
        ),
        "coriolis_zetas.csv": (
            [
                "mode_i_zero_based",
                "mode_j_zero_based",
                "rotational_axis",
                "value_dimensionless",
            ],
            data.n_modes**2 * 3,
        ),
        "metadata.csv": (["key", "value"], 1 + len(data.metadata)),
    }

    assert {path.name for path in paths} == set(expected_shapes)
    for name, (headers, row_count) in expected_shapes.items():
        with (tmp_path / "csv" / name).open(newline="", encoding="utf-8") as stream:
            rows = list(csv.reader(stream))
        assert rows[0] == headers
        assert len(rows) == row_count + 1
        assert all(row for row in rows[1:])
