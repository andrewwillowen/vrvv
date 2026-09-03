# CFOUR data ingestion

The CFOUR ingest plugin reads the output files from an anharmonic
vibration-rotation calculation and separates source-faithful parsing from
normalization. Parsing preserves the values and one-indexed CFOUR mode
numbers in the source files. Normalization constructs the dense, zero-indexed
core quantities used by downstream calculations.

## Required files

`CFOURParser` accepts a directory only when it contains all four of these
files:

| File | Parsed quantity | Source layout |
| --- | --- | --- |
| `anharm.out` | Equilibrium rotational constants and harmonic frequencies | Text sections in the main CFOUR output |
| `corioliszeta` | Coriolis zeta couplings | One lower-triangular matrix per Cartesian axis |
| `cubic` | Cubic force constants | One permutation-unique entry per mode triple |
| `didQ` | Inertia-derivative data used to form rotational derivatives | A complete 3 by 3 Cartesian matrix for each vibrational mode |

Missing files are an error. The plugin does not infer values from an
alternative CFOUR output or silently select another parser.

## Indexing conventions

CFOUR vibrational mode numbers in these files are one-indexed. For a
nonlinear molecule, they begin after the six translational and rotational
degrees of freedom; the current parser records the first vibrational mode as
CFOUR index 7.

Raw parser objects retain those source indices. Normalized core quantities
renumber vibrational modes densely from zero:

$$
i_\text{core} = i_\text{CFOUR} - i_\text{first vibrational mode}.
$$

Thus, with the current CFOUR convention, source mode 7 becomes core mode 0.
Cartesian axes are likewise converted from CFOUR's one-indexed 1, 2, 3 to
zero-indexed X, Y, Z positions.

## `anharm.out`

### Equilibrium rotational constants

The `Be` row in the `Be, B0 AND B-B0 SHIFTS ... (MHz)` section supplies the
equilibrium rotational constants $B_X$, $B_Y$, and $B_Z$ in MHz.

| Core unit | Conversion from source MHz |
| --- | --- |
| Hz | $B_\text{Hz} = 10^6 B_\text{CFOUR}$ |

The normalized core representation is Hz.

### Harmonic frequencies

The harmonic-frequency column in `HARMONIC AND FUNDAMENTAL FREQUENCIES
(cm-1) ...` is in $\mathrm{cm}^{-1}$.

| Core unit | Conversion from source $\mathrm{cm}^{-1}$ |
| --- | --- |
| Hz | $\nu_\text{Hz} = 100c\tilde{\nu}_\text{CFOUR}$ |

Normalization stores modes in increasing harmonic frequency order and checks
that this ordering is preserved.

## `corioliszeta`

Each section supplies the lower-triangular entries of one Coriolis zeta
matrix, $\zeta^\alpha_{ij}$, for Cartesian axis $\alpha \in \{X,Y,Z\}$.
Zeta couplings are dimensionless, so normalization makes no unit conversion.

The normalized form is a dense square matrix per axis. The values satisfy

$$
\zeta^\alpha_{ij} = -\zeta^\alpha_{ji},
\qquad
\zeta^\alpha_{ii} = 0.
$$

For each source entry, normalization inserts the reported lower-triangular
value and its negative at the transposed position.

## `cubic`

The `cubic` file reports a cubic force constant for each unique unordered
mode triple. The legacy implementation treats the source values as
$\mathrm{cm}^{-1}$ and converts them to Hz for calculations:

$$
k_{ijk,\mathrm{Hz}} = 100c\,k_{ijk,\mathrm{cm}^{-1}}.
$$

Normalization expands every reported value to the full dense tensor:

$$
k_{ijk} = k_{\pi(i)\pi(j)\pi(k)}
$$

for every permutation $\pi$ of the three mode indices. The normalized tensor
therefore has shape `(n_modes, n_modes, n_modes)` and is invariant under
permutation of its axes.

## `didQ`

Each `didQ` row contains two Cartesian indices, a CFOUR vibrational-mode
index, and a value. Unlike `cubic`, all nine Cartesian entries are present
for each mode. Normalization reshapes the entries into a tensor with shape
`(n_modes, 3, 3)`:

$$
a_k^{\alpha\beta},
$$

where $k$ is a vibrational mode and $\alpha,\beta$ are rotational Cartesian
axes. This is the inertia-derivative quantity used to construct the
vibration-rotation rotational derivatives. It should be symmetric in the
Cartesian indices:

$$
a_k^{\alpha\beta} = a_k^{\beta\alpha}.
$$

Normalization converts each raw value using

$$
a_{k,\mathrm{SI}}^{\alpha\beta}
= a_{k,\mathrm{raw}}^{\alpha\beta}
\sqrt{\mathrm{amu}}\,a_0,
$$

where $a_0$ is the Bohr radius. That produces units of
$\mathrm{kg}^{1/2}\,\mathrm{m}$ if the raw values are in
$(\mathrm{amu})^{1/2}\,a_0$ units.

The resulting rotational derivative can be represented in Hz as

$$
B_{k,\mathrm{Hz}}^{\alpha\beta}
= -\frac{\hbar^3}{2h^{3/2}}
\frac{a_k^{\alpha\beta}}
{I_\alpha^0 I_\beta^0\sqrt{\nu_k}}.
$$
