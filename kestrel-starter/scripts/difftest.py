#!/usr/bin/env python3
"""Differential end-to-end test: Python Kestrel vs the TypeScript port.

    python scripts/difftest.py "gray|threshold:128"

Runs the pipeline spec on every file in samples/ twice, with
`python -m kestrel.cli` and with `npx tsx src/cli.ts` (from ts/), then compares
exit codes and output bytes. Outputs keep the input's extension. Exit 0 when
every sample matches, 1 on any mismatch, 2 when the TS CLI cannot run yet.
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TS = ROOT / "ts"
SAMPLES = ROOT / "samples"
NEEDS = "pipeline/runner, pipeline/steps, every ops module, io/ppm, io/pgm and cli"
HEADER = ("sample", "python", "typescript", "result")


def run(cmd: list[str], cwd: Path, out: Path) -> tuple[int, bytes | None]:
    """Run one CLI; return its exit code and the output file's bytes (None if absent)."""
    proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=120)
    if proc.returncode not in (0, 1, 2):
        sys.stderr.write(proc.stderr.decode(errors="replace")[-500:])
    return proc.returncode, out.read_bytes() if out.exists() else None


def describe(result: tuple[int, bytes | None]) -> str:
    code, data = result
    return f"exit {code}, {len(data)} bytes" if data is not None else f"exit {code}, no output"


def verdict(py: tuple[int, bytes | None], ts: tuple[int, bytes | None]) -> str:
    if py == ts:
        return "match"
    a, b = py[1] or b"", ts[1] or b""
    if py[0] != ts[0] or py[1] is None or ts[1] is None:
        return "MISMATCH (exit code or missing output)"
    first = next((i for i, (x, y) in enumerate(zip(a, b, strict=False)) if x != y), min(len(a), len(b)))
    return f"MISMATCH (first difference at byte {first})"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("spec", help='pipeline spec, e.g. "gray|threshold:128"')
    spec = parser.parse_args(argv).spec

    if not (TS / "src" / "cli.ts").exists():
        print(f"TS CLI not ported yet: ts/src/cli.ts is missing.\ndifftest needs {NEEDS} ported first.")
        return 2
    if not (TS / "node_modules" / ".bin" / "tsx").exists():
        print("tsx is not installed: run (cd ts && npm ci) first.")
        return 2

    rows, mismatches = [], 0
    with tempfile.TemporaryDirectory() as tmp:
        for sample in sorted(SAMPLES.iterdir()):
            if sample.suffix not in (".ppm", ".pgm"):
                continue
            py_out = Path(tmp) / f"py-{sample.name}"
            ts_out = Path(tmp) / f"ts-{sample.name}"
            py = run([sys.executable, "-m", "kestrel.cli", str(sample), str(py_out), spec], ROOT, py_out)
            ts = run(["npx", "tsx", "src/cli.ts", str(sample), str(ts_out), spec], TS, ts_out)
            mismatches += py != ts
            rows.append((sample.name, describe(py), describe(ts), verdict(py, ts)))

    widths = [max(len(r[i]) for r in [HEADER, *rows]) for i in range(4)]
    for r in [HEADER, *rows]:
        print("  ".join(c.ljust(w) for c, w in zip(r, widths, strict=True)).rstrip())
    print(f"\n{len(rows) - mismatches}/{len(rows)} samples match for spec {spec!r}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
