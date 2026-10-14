# Kestrel starter

A practice sandbox: a 24-module slice of Kestrel, a fictional pure-Python image-processing library.

## Goal

Port `kestrel/` to TypeScript in `ts/`, keeping behaviour identical: same results, same errors, same output bytes.

## Rules

- Read `MIGRATION.md` before porting anything. It defines file mapping, naming, types, test porting and known traps.
- A module is done only when `scripts/verify.sh kestrel/<path>.py` exits 0. Do not report a module as done otherwise.
- Never edit Python sources (`kestrel/`) or Python tests (`tests/`). They are the specification.
- Port a module only after its dependencies are ported: `python scripts/status.py --next` lists the ready ones, `python scripts/deps.py --layers` shows the waves.
- `python scripts/status.py` is the source of truth for progress, not anyone's report.
- When you discover a Python-vs-TypeScript behaviour difference, add one bullet to "Known traps" in `MIGRATION.md`.
