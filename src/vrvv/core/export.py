"""Export canonical quantities to CSV files."""

import csv
from pathlib import Path
from typing import Iterable

from vrvv.core.quantities import StandardData


def _write_csv(
    path: Path, headers: list[str], rows: Iterable[Iterable[object]]
) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)


def export_standard_data(data: StandardData, output_dir: Path) -> list[Path]:
    """Write each component of ``data`` to a clearly labelled CSV file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    axes = ("X", "Y", "Z")
    paths: list[Path] = []

    path = output_dir / "equilibrium_rotational_constants.csv"
    _write_csv(
        path,
        ["rotational_axis", "value_hz"],
        (
            (axis, value)
            for axis, value in zip(
                axes, data.equilibrium_rotational_constants.values, strict=True
            )
        ),
    )
    paths.append(path)

    path = output_dir / "harmonic_frequencies.csv"
    _write_csv(
        path,
        ["mode_index_zero_based", "frequency_hz"],
        (
            (index, value)
            for index, value in enumerate(data.harmonic_frequencies.values)
        ),
    )
    paths.append(path)

    path = output_dir / "cubic_force_constants.csv"
    _write_csv(
        path,
        [
            "mode_i_zero_based",
            "mode_j_zero_based",
            "mode_k_zero_based",
            "value_hz",
        ],
        (
            (i, j, k, data.cubic_force_constants.values[i, j, k])
            for i in range(data.n_modes)
            for j in range(data.n_modes)
            for k in range(data.n_modes)
        ),
    )
    paths.append(path)

    for name, values, unit in (
        (
            "inertial_derivatives",
            data.inertial_derivatives.values,
            "value_kg^0.5_m",
        ),
        ("rotational_derivatives", data.rotational_derivatives.values, "value_hz"),
    ):
        path = output_dir / f"{name}.csv"
        _write_csv(
            path,
            ["mode_index_zero_based", "axis_alpha", "axis_beta", unit],
            (
                (mode, axes[alpha], axes[beta], values[mode, alpha, beta])
                for mode in range(data.n_modes)
                for alpha in range(3)
                for beta in range(3)
            ),
        )
        paths.append(path)

    path = output_dir / "coriolis_zetas.csv"
    _write_csv(
        path,
        [
            "mode_i_zero_based",
            "mode_j_zero_based",
            "rotational_axis",
            "value_dimensionless",
        ],
        (
            (i, j, axes[axis], data.coriolis_zetas.values[i, j, axis])
            for i in range(data.n_modes)
            for j in range(data.n_modes)
            for axis in range(3)
        ),
    )
    paths.append(path)

    path = output_dir / "metadata.csv"
    _write_csv(
        path,
        ["key", "value"],
        [("n_modes", data.n_modes), *data.metadata.items()],
    )
    paths.append(path)
    return paths
