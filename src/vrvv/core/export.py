"""Export canonical quantities to CSV files."""

import csv
import math
from collections.abc import Iterable
from pathlib import Path

from vrvv.core.quantities import StandardData
from vrvv.core.units import WAVENUMBER_TO_HZ


def _write_csv(
    path: Path, headers: list[str], rows: Iterable[Iterable[object]]
) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)


def _standard_data_tables(
    data: StandardData,
) -> Iterable[tuple[str, list[str], Iterable[Iterable[object]]]]:
    """Yield the component tables shared by CSV and Excel exports."""
    axes = ("X", "Y", "Z")
    yield (
        "equilibrium_rotational_constants",
        ["rotational_axis", "value_hz"],
        (
            (axis, value)
            for axis, value in zip(
                axes, data.equilibrium_rotational_constants.values, strict=True
            )
        ),
    )
    yield (
        "harmonic_frequencies",
        ["mode_index_zero_based", "frequency_hz"],
        (
            (index, value)
            for index, value in enumerate(data.harmonic_frequencies.values)
        ),
    )
    yield (
        "cubic_force_constants",
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

    for name, values, unit in (
        (
            "inertial_derivatives",
            data.inertial_derivatives.values,
            "value_kg^0.5_m",
        ),
        ("rotational_derivatives", data.rotational_derivatives.values, "value_hz"),
    ):
        yield (
            name,
            ["mode_index_zero_based", "axis_alpha", "axis_beta", unit],
            (
                (mode, axes[alpha], axes[beta], values[mode, alpha, beta])
                for mode in range(data.n_modes)
                for alpha in range(3)
                for beta in range(3)
            ),
        )
    yield (
        "coriolis_zetas",
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
    yield (
        "metadata",
        ["key", "value"],
        [("n_modes", data.n_modes), *data.metadata.items()],
    )


def export_standard_data(data: StandardData, output_dir: Path) -> list[Path]:
    """Write each component of ``data`` to a clearly labelled CSV file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for name, headers, rows in _standard_data_tables(data):
        path = output_dir / f"{name}.csv"
        _write_csv(path, headers, rows)
        paths.append(path)
    return paths


def export_standard_data_excel(data: StandardData, output_path: Path) -> Path:
    """Write each canonical component to a worksheet in an Excel workbook."""
    from openpyxl import Workbook  # type: ignore[import-untyped]

    output_path = Path(output_path)
    workbook = Workbook(write_only=True)
    for name, headers, rows in _standard_data_tables(data):
        worksheet_name = (
            "equilibrium_rotational_consts"
            if name == "equilibrium_rotational_constants"
            else name
        )
        worksheet = workbook.create_sheet(title=worksheet_name)
        worksheet.append(headers)
        for row in rows:
            worksheet.append(
                [str(value) if isinstance(value, Path) else value for value in row]
            )
    workbook.save(output_path)
    return output_path


def _dat_metadata_text(data: StandardData, key: str, default: str) -> str:
    """Return one DAT metadata record, rejecting values Fortran cannot read."""
    value = data.metadata.get(key, default)
    if not isinstance(value, str):
        raise TypeError(f"DAT metadata '{key}' must be a string")
    if len(value) > 76:
        raise ValueError(f"DAT metadata '{key}' must be at most 76 characters")
    return value


def _dat_metadata_mode(data: StandardData, key: str, default: int) -> int:
    """Return a one-based resonance-mode index."""
    value = data.metadata.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"DAT metadata '{key}' must be an integer")
    if not 1 <= value <= data.n_modes:
        raise ValueError(
            f"DAT metadata '{key}' must be between 1 and {data.n_modes}, got {value}"
        )
    return value


def _dat_atom_count(data: StandardData) -> int:
    """Validate the molecular metadata required by the DAT header."""
    n_atoms = data.metadata.get("n_atoms")
    is_linear = data.metadata.get("is_linear")
    if isinstance(n_atoms, bool) or not isinstance(n_atoms, int):
        raise TypeError("DAT export requires integer metadata 'n_atoms'")
    if n_atoms <= 0:
        raise ValueError("DAT export requires positive metadata 'n_atoms'")
    if not isinstance(is_linear, bool):
        raise TypeError("DAT export requires boolean metadata 'is_linear'")
    expected_modes = 3 * n_atoms - (5 if is_linear else 6)
    if data.n_modes != expected_modes:
        raise ValueError(
            "DAT metadata is inconsistent: "
            f"n_modes={data.n_modes}, n_atoms={n_atoms}, is_linear={is_linear}"
        )
    return n_atoms


def _format_dat_float(value: float, fractional_digits: int) -> str:
    """Render a finite value with maximal precision in a 12-character field."""
    if not math.isfinite(value):
        raise ValueError("DAT export values must be finite")
    for digits in range(fractional_digits, -1, -1):
        formatted = f"{value:12.{digits}f}"
        if len(formatted) == 12:
            return formatted
    raise ValueError(
        f"DAT value cannot be represented in a 12-character field: {value}"
    )


def _write_dat_values(stream, values: Iterable[float], fractional_digits: int) -> None:
    """Write DAT numeric records with at most six fixed-width fields."""
    row: list[str] = []
    for value in values:
        row.append(_format_dat_float(float(value), fractional_digits))
        if len(row) == 6:
            stream.write("".join(row) + "\n")
            row = []
    if row:
        stream.write("".join(row) + "\n")


def export_standard_data_dat(data: StandardData, output_path: Path) -> Path:
    """Write ``data`` in the fixed-width legacy Fortran DAT interchange format."""
    output_path = Path(output_path)
    n_atoms = _dat_atom_count(data)
    resonance_a = _dat_metadata_mode(data, "dat_resonance_a_mode", 1)
    resonance_b = _dat_metadata_mode(data, "dat_resonance_b_mode", 2)
    if resonance_a == resonance_b:
        raise ValueError("DAT resonance mode indices must be distinct")

    metadata_records = (
        _dat_metadata_text(data, "dat_title", "vrvv StandardData export"),
        _dat_metadata_text(
            data, "dat_program", str(data.metadata.get("source_type", "vrvv"))
        ),
        _dat_metadata_text(data, "dat_method", "unknown"),
        _dat_metadata_text(data, "dat_basis", "unknown"),
        _dat_metadata_text(
            data, "dat_resonance_a_description", "Unspecified resonance A"
        ),
        _dat_metadata_text(
            data, "dat_resonance_b_description", "Unspecified resonance B"
        ),
    )

    with output_path.open("w", encoding="ascii", newline="\n") as stream:
        stream.write(f"{n_atoms:4d}{data.n_modes:4d}{resonance_a:4d}{resonance_b:4d}\n")
        for record in metadata_records:
            stream.write(f"{record:<76}\n")

        _write_dat_values(
            stream, data.harmonic_frequencies.values / WAVENUMBER_TO_HZ, 4
        )
        _write_dat_values(
            stream,
            data.equilibrium_rotational_constants.values / WAVENUMBER_TO_HZ,
            8,
        )
        _write_dat_values(
            stream,
            (
                value / WAVENUMBER_TO_HZ
                for value in data.cubic_force_constants.values.ravel(order="F")
            ),
            8,
        )
        for axis in range(3):
            _write_dat_values(stream, data.coriolis_zetas.values[:, :, axis].flat, 9)
        c_values = (
            -data.rotational_derivatives.values
            / data.harmonic_frequencies.values[:, None, None]
        )
        for alpha, beta in ((0, 0), (1, 1), (2, 2), (0, 1), (1, 2), (2, 0)):
            _write_dat_values(stream, c_values[:, alpha, beta], 9)
    return output_path
