# kestrel-starter

Practice sandbox for the course **"Scaling Agents: From One to One Hundred"**. Nothing here is production code. Break it, reset it, port it again.

**Kestrel** is a fictional open-source image-processing library written in pure Python. In the course's story, the real Kestrel has about 240 modules and the team is porting it to TypeScript. This repo is a 24-module slice of it, small enough that every lab runs for real at low cost. Your agents port `kestrel/` to `ts/`, keeping behaviour byte-for-byte identical.

Images are deliberately simple: an `Image` has a `width`, a `height` and a flat, row-major list of `(r, g, b)` integer tuples in 0..255. No numpy, no PIL.

## Prerequisites

- Python 3.11+
- Node.js 22.12+ (with npm)
- Claude Code

## Setup

```bash
git init && git add -A && git commit -m "Kestrel starter"
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install pytest
cd ts && npm ci && cd ..
```

Your copy of this folder starts without git history of its own, so the first line makes the starting commit. The worktree labs need it.

`npm ci` installs exactly what `ts/package-lock.json` pins, so everyone gets the same TypeScript toolchain (TypeScript, vitest, tsx).

## Layout

```
kestrel/          the Python library (24 modules): core/, ops/, io/, analysis/, pipeline/, cli.py
tests/            pytest tests, mirroring kestrel/ (tests/core/test_color.py, ..., tests/test_cli.py)
ts/               the TypeScript port: ts/src/<same path>.ts, ts/test/<same path>.test.ts
samples/          tiny .ppm / .pgm images for end-to-end checks
scripts/          deps.py, status.py, verify.sh, difftest.py
MIGRATION.md      the porting rules, plus a "Known traps" section you fill in
CLAUDE.md         the short guide Claude Code reads at the start of every session
.claude/          settings.json (pre-approved test commands), agents/ and workflows/ (empty, for you)
```

## Running the tests

```bash
python -m pytest -q                              # all Python tests (they pass out of the box)
cd ts && npx vitest run test/core/color.test.ts  # one ported TS test file
cd ts && npm test                                # every TS test
```

Until the first module is ported, `npm test` reports "No test files found" and exits 1. That is expected.

Try the Python CLI:

```bash
python -m kestrel.cli samples/tiny.ppm /tmp/out.ppm "gray|threshold:128"
python -m kestrel.cli samples/gradient.ppm /tmp/out.ppm "crop:0,0,4,2|blur:1|pad:1,wrap"
```

Steps: `blur:r`, `brightness:d`, `contrast:f`, `crop:x,y,w,h`, `equalize`, `flip:h|v`, `gray`, `invert`, `pad:n[,constant|edge|wrap]`, `resize:w,h`, `rotate:turns`, `threshold:level`.

## Scripts

| Command | What it does |
|---|---|
| `python scripts/deps.py` | Module dependency graph from the imports, as adjacency JSON |
| `python scripts/deps.py --layers` | Topological waves L0..L6: every module in a wave depends only on earlier waves |
| `python scripts/deps.py --critical` | The longest dependency chain (critical path) |
| `python scripts/deps.py --dot` | Graphviz source (`... --dot \| dot -Tsvg > deps.svg`) |
| `python scripts/status.py` | Table of every module: ported? TS test present? TS test passing? |
| `python scripts/status.py --json` | The same as JSON, for scripts and agents |
| `python scripts/status.py --next` | Modules not yet ported whose dependencies are all ported |
| `python scripts/status.py --no-run` | Table without running vitest (fast) |
| `scripts/verify.sh kestrel/core/color.py` | Runs that module's Python tests and its TS tests; exit 0 only if both pass. The definition of done |
| `python scripts/difftest.py "gray\|threshold:128"` | Runs a pipeline on every sample with Python and with the TS CLI (`ts/src/cli.ts`) and compares output bytes |

`verify.sh` also checks that the TS test file contains every Python test name, so a port cannot pass by dropping the cases that fail.

## Resetting

This is a git repository with a single commit, "Kestrel starter". `git stash -u` or `git reset --hard && git clean -fd -e ts/node_modules -e .venv` takes you back to the start.
