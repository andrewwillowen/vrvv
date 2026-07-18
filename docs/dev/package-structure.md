# Package Structure

This project is being rebuilt as both a Python library and a CLI, with the scientific backend as the source of truth and the CLI as a thin user-facing interface.

## Architectural Layers

- `vrvv/core/`: foundational typed objects and low-level reusable components (the "nouns")
- `vrvv/compute/`: high-level operations/workflows that transform core objects (the "verbs")
- `vrvv/ingest/`: parser adapters, parser registry, and normalization of parsed data
- `vrvv/cli/`: Typer interface and command wiring only (no nontrivial business logic)

## Data Model 

- Treat both symbolic and numeric Hamiltonian representations as first-class concepts.
- Keep parser-specific raw data available for inspection/debugging.
- Normalize parser outputs into standard typed objects before compute workflows consume them.
- Default CLI output should show normalized quantities; raw parser data should be opt-in.

## Parser Strategy

- Use a pluggable parser registry so new source programs can be added without touching `core`/`compute`.
- Keep parser-specific details at the ingest boundary.

## Logging Strategy

- Use centralized Loguru configuration (for example in `vrvv/logging.py`).
- CLI startup calls `configure_logging(...)`.
- Library modules import `logger` directly from Loguru and do not configure logging on import.
- Library users can optionally call `vrvv.configure_logging(...)` to get CLI-style logging behavior.
- For recursive compute workflows, keep detailed call-path logging at `DEBUG`/`TRACE`, with concise progress at `INFO`.
