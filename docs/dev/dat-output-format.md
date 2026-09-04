# Legacy DAT output format

`vrvv parse cfour <directory> --to-dat output.dat` writes normalized
`StandardData` in the sequential fixed-width layout read by
`scripts/claudes-fortran/commutator(3).f90`. It is intended for exchange with
that legacy calculation, not as a general-purpose data format.

## File layout

The first record contains four `I4` integer fields: number of atoms, number
of vibrational modes, and the two resonant modes. Resonant modes are
one-based in this file even though core arrays use zero-based mode indices.
It is followed by six 76-character text records: title, source program,
method, basis, and descriptions for resonances A and B.

All remaining values use `F12.6` fields with up to six values per physical
record, in this order:

1. Harmonic frequencies.
2. Equilibrium rotational constants in X, Y, Z axis order.
3. The full cubic force-constant tensor, in Fortran column-major array order.
4. Three dense Coriolis-zeta matrices, in X, Y, Z order; each matrix is
   written row by row.
5. Six dimensionless C vectors derived from rotational derivatives:
   `aa`, `bb`, `cc`, `ab`, `bc`, then `ca`.

## Units

| DAT block | Units |
| --- | --- |
| Header: `Natom`, `Nvibs`, `A`, `B` | Integer counts and one-based mode indices |
| Six metadata records | Text |
| `omega` harmonic frequencies | cm<sup>-1</sup> |
| `ABC` equilibrium rotational constants | cm<sup>-1</sup> |
| `k_cubic` cubic force constants | cm<sup>-1</sup> |
| `zeta` Coriolis coupling matrices | Dimensionless |
| `Caa`, `Cbb`, `Ccc`, `Cab`, `Cbc`, `Cca` | Dimensionless |

The legacy source explicitly describes `omega`, `ABC`, and `k_cubic` as
wavenumber quantities, and zetas as dimensionless. `vrvv` therefore converts
the corresponding canonical Hz values to cm<sup>-1</sup> by dividing by
`WAVENUMBER_TO_HZ`, and writes zetas unchanged.

The C block follows the reference relation
\(C_k^{\alpha\beta} = -B_k^{\alpha\beta}/\nu_k\).

## Color-coded minimal example

This illustrative file uses three nonlinear-molecule vibrational modes. It is
shortened after the first entries of repeated tensor blocks: a real DAT file
contains every value required by its declared `Nvibs`.

<pre><span style="color: #7c3aed; font-weight: bold">   3   3   1   2</span> <span style="color: #6b7280; font-style: italic"># Header: Natom, Nvibs, A, B</span>
<span style="color: #0369a1; font-weight: bold">Example nonlinear molecule</span> <span style="color: #6b7280; font-style: italic"># Title</span>
<span style="color: #0369a1; font-weight: bold">CFOUR</span> <span style="color: #6b7280; font-style: italic"># Program</span>
<span style="color: #0369a1; font-weight: bold">CCSD(T)</span> <span style="color: #6b7280; font-style: italic"># Method</span>
<span style="color: #0369a1; font-weight: bold">cc-pVDZ</span> <span style="color: #6b7280; font-style: italic"># Basis</span>
<span style="color: #0369a1; font-weight: bold">Mode 1 resonance</span> <span style="color: #6b7280; font-style: italic"># A description</span>
<span style="color: #0369a1; font-weight: bold">Mode 2 resonance</span> <span style="color: #6b7280; font-style: italic"># B description</span>
<span style="color: #b45309; font-weight: bold">  500.000000  750.000000 1000.000000</span> <span style="color: #6b7280; font-style: italic"># omega, cm^-1</span>
<span style="color: #047857; font-weight: bold">    0.200000    0.300000    0.500000</span> <span style="color: #6b7280; font-style: italic"># ABC, cm^-1</span>
<span style="color: #be123c; font-weight: bold">   -1.000000    0.000000    0.000000 ...</span> <span style="color: #6b7280; font-style: italic"># k_cubic, cm^-1; full 3 x 3 x 3 tensor</span>
<span style="color: #6d28d9; font-weight: bold">    0.000000    0.100000   -0.100000</span> <span style="color: #6b7280; font-style: italic"># zeta X, dimensionless</span>
<span style="color: #6d28d9; font-weight: bold">   -0.100000    0.000000    0.200000</span>
<span style="color: #6d28d9; font-weight: bold">    0.100000   -0.200000    0.000000</span>
<span style="color: #6d28d9; font-weight: bold">    ...</span> <span style="color: #6b7280; font-style: italic"># zeta Y, then zeta Z</span>
<span style="color: #b91c1c; font-weight: bold">    0.010000    0.020000    0.030000</span> <span style="color: #6b7280; font-style: italic"># Caa, dimensionless</span>
<span style="color: #b91c1c; font-weight: bold">    ...</span> <span style="color: #6b7280; font-style: italic"># Cbb, Ccc, Cab, Cbc, Cca follow</span></pre>

Colors identify file regions only; the comments and ellipses are explanatory
and **must not** appear in an exported DAT file. Every actual numeric field is
fixed-width `F12.6`, and the six text records are each 76 characters wide.

## Metadata

DAT-specific metadata is stored in `StandardData.metadata`. Each text value
must be a string no longer than 76 characters:

| Key | Default |
| --- | --- |
| `dat_title` | `vrvv StandardData export` |
| `dat_program` | `source_type`, or `vrvv` |
| `dat_method` | `unknown` |
| `dat_basis` | `unknown` |
| `dat_resonance_a_description` | `Unspecified resonance A` |
| `dat_resonance_b_description` | `Unspecified resonance B` |
| `dat_resonance_a_mode` | `1` |
| `dat_resonance_b_mode` | `2` |

Resonance mode metadata must be distinct integers between `1` and `n_modes`.
Datasets with fewer than two modes therefore require no exportable default.

The header also requires `n_atoms` and `is_linear` metadata. CFOUR ingestion
populates both from `anharm.out` and validates either the nonlinear
relationship `n_modes = 3*n_atoms - 6` or the linear relationship
`n_modes = 3*n_atoms - 5`.

## Linear-molecule compatibility

The Python DAT writer supports both validated molecular classes. The supplied
legacy Fortran reader subsequently overwrites its read `Nvibs` value with
`3*Natom - 6`, so it cannot correctly consume linear-molecule files without
a corresponding Fortran change.
