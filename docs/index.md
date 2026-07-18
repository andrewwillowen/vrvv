# vrvv

Python implementation of the vibration-rotation Van Vleck perturbation theory approach
for deriving predictions of vibration-rotation interactions in small molecules.

## Getting started

### Installation

!!! warning
    
    This package is under active development - functionality is subject to change
    without notice (!).

Install the package using `pip` (requires `python >= 3.13`), `pipx`, or `uv`:

```bash
python3 -m pip install "git+https://github.com/andrewwillowen/vrvv.git@main"
```

```bash
pipx install "git+https://github.com/andrewwillowen/vrvv.git@main"
```

```bash
uv tool install "git+https://github.com/andrewwillowen/vrvv.git@main"
```

### The vrvv command

Once installed, run the command `vrvv` to see the help text.

```bash
vrvv
```

### The vrvv Python module

Eventually, you can write your own Python code on top of the vrvv package with

```python
import vrvv
```

## About

The work of this project is based on the final thesis chapter from the PhD defense of the author, Andrew N. Owen.

For now, to understand the purpose and foundation of this work, you should read the introduction of the chapter.

**Bibtex citation**

``` { .bibtex .copy }
@phdthesis{
    Owen, 2022,
    author={Owen,Andrew N.},
    year={2022},
    title={Computational Methods Applied to the Study of the Structure, Spectra, and Reactivity of Small Organic Molecules},
    journal={ProQuest Dissertations and Theses},
    pages={424},
    note={Copyright - Database copyright ProQuest LLC; ProQuest does not claim copyright in the individual underlying works; Last updated - 2023-03-08},
    isbn={9798841766650},
    language={English},
    url={https://www.proquest.com/dissertations-theses/computational-methods-applied-study-structure/docview/2703382999/se-2}
}
```
