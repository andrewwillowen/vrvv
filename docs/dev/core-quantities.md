# Core quantities

`vrvv.core.quantities` defines canonical, program-independent data objects.
Ingest plugins must convert source-specific output into these objects;
compute workflows must depend on this representation rather than an input
program's file layouts or indexing conventions.

All normalized vibrational-mode arrays use dense, zero-based indices. Mode 0
is the lowest-frequency vibrational mode included in the dataset.

## `StandardData`

`StandardData` is the top-level canonical container returned by an ingest
normalizer. It contains `equilibrium_rotational_constants`,
`harmonic_frequencies`, `cubic_force_constants`, `inertial_derivatives`,
`rotational_derivatives`, and `coriolis_zetas`, plus optional source
`metadata`. Its required `n_modes` value is the shared number of vibrational
modes; construction validates that every mode-indexed quantity has that
length.

`StandardData.to_csv(output_dir)` exports each component to a separate CSV
file. The files use dense zero-based mode indices and include units in their
value column headings; `metadata.csv` contains `n_modes` and source metadata.
For example, normalized CFOUR data can be exported from the command line with:

```console
vrvv parse cfour <directory> --to-csv <output-directory>
```

`StandardData.to_dat(output_path)` writes one fixed-width legacy Fortran DAT
file. It is available from the CLI with:

```console
vrvv parse cfour <directory> --to-dat output.dat
```

See [Legacy DAT output format](dat-output-format.md) for its record sequence,
metadata keys, and unit conversions.

`StandardData.to_excel(output_path)` writes the same component tables as the
CSV export to separate worksheets in one Excel workbook. The
`equilibrium_rotational_constants` CSV table uses the shortened worksheet name
`equilibrium_rotational_consts` because Excel worksheet names are limited to
31 characters:

```console
vrvv parse cfour <directory> --to-excel normalized-data.xlsx
```

## Equilibrium rotational constants

`EquilibriumRotationalConstants` holds a one-dimensional `values` array with
shape `(3,)` in Hz. Its entries are ordered by Cartesian principal axis:
`values[0]` is X, `values[1]` is Y, and `values[2]` is Z. Read-only `X`, `Y`,
and `Z` properties provide named access to those entries.

| Type | Component unit |
| --- | --- |
| `EquilibriumRotationalConstants` | Hz |

## Harmonic frequencies

`HarmonicFrequencies` holds a one-dimensional `values` array in Hz.
`values[k]` is the harmonic frequency of zero-indexed vibrational mode $k$.

| Type | Array unit | Required invariants |
| --- | --- | --- |
| `HarmonicFrequencies` | Hz | One-dimensional; non-decreasing |

## Coriolis zeta couplings

`CoriolisZetas` holds a dense dimensionless `values` tensor with shape
`(n_modes, n_modes, 3)`. The first two axes are vibrational modes; the final
axis is the rotational Cartesian axis ordered X, Y, Z. Read-only `X`, `Y`,
and `Z` properties provide the corresponding `(n_modes, n_modes)` matrices.
For every axis $\alpha$, the tensor must be antisymmetric in its vibrational
indices:

$$
\zeta^\alpha_{ij} = -\zeta^\alpha_{ji}.
$$

The dataclass validates equal-length vibrational axes and antisymmetry,
including a zero diagonal within numerical tolerance.

## Cubic force constants

`CubicForceConstants` holds a dense `values` array in Hz with shape
`(n_modes, n_modes, n_modes)`.

| Type | Array unit |
| --- | --- |
| `CubicForceConstants` | Hz |

The tensor must be fully symmetric:

$$
k_{ijk} = k_{\pi(i)\pi(j)\pi(k)}
$$

for every permutation $\pi$ of its three mode indices. The dataclasses
validate that all three dimensions have equal length and that the tensor is
invariant under every axis permutation.

## Inertial and rotational derivatives

`InertialDerivatives` represents $a_k^{\alpha\beta}$ in
$\mathrm{kg}^{1/2}\,\mathrm{m}$. `RotationalDerivatives` represents the
corresponding $B_k^{\alpha\beta}$ in Hz. These correspond to the values
defined in Section 15.1 of Papousek and Aliev.[^papousek-aliev-1982]

Both types are intended to hold a dense `values` array with shape
`(n_modes, 3, 3)`. The first axis selects vibrational mode $k$; the final two
select rotational Cartesian axes $\alpha$ and $\beta$. Both tensors must be
symmetric in the rotational indices:

$$
a_k^{\alpha\beta} = a_k^{\beta\alpha},
\qquad
B_k^{\alpha\beta} = B_k^{\beta\alpha}.
$$

With $\nu_k$ in Hz and $I^0_\alpha$, $I^0_\beta$ in
$\mathrm{kg\,m^2}$, the core quantities are related by

$$
B_{k,\mathrm{Hz}}^{\alpha\beta}
= -\frac{\hbar^3}{2h^{3/2}}
\frac{a_k^{\alpha\beta}}
{I_\alpha^0 I_\beta^0\sqrt{\nu_k}}.
$$

[^papousek-aliev-1982]: D. Papousek and M. R. Aliev, *Molecular
    Vibrational-Rotational Spectra: Theory and Applications of High Resolution
    Infrared, Microwave, and Raman Spectroscopy of Polyatomic Molecules*,
    Elsevier Scientific Publishing Company, New York (1982), Section 15.1.
