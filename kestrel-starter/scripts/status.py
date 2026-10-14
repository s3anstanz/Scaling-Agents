#!/usr/bin/env python3
"""Port status of every Kestrel module, derived from the files in the repo.

    python scripts/status.py            aligned table
    python scripts/status.py --json     JSON list, one object per module
    python scripts/status.py --next     modules not yet ported whose deps are all ported
    python scripts/status.py --no-run   skip running vitest (ts_tests_pass becomes null)

Per module: py path, ts path (ts/src/<id>.ts), ts test path (ts/test/<id>.test.ts),
ported (the ts file exists), ts_test_present, and ts_tests_pass:
true / false after running vitest, "unknown" if npx is missing or vitest could
not report, null when there is no TS test or --no-run was given.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deps import ROOT, depths, graph

TS = ROOT / "ts"


def run_vitest(test_files: list[str]) -> dict[str, bool] | None:
    """Run vitest once on the given ts/-relative files; map each file to pass/fail."""
    if not test_files or shutil.which("npx") is None:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "report.json"
        subprocess.run(["npx", "vitest", "run", "--reporter=json", f"--outputFile={report}", *test_files],
                       cwd=TS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
        if not report.exists():
            return None
        results = json.loads(report.read_text(encoding="utf-8")).get("testResults", [])
    outcome = {Path(r["name"]).resolve(): r.get("status") == "passed" for r in results}
    return {f: outcome[(TS / f).resolve()] for f in test_files if (TS / f).resolve() in outcome}


def collect(run_tests: bool) -> list[dict]:
    g = graph()
    d = depths(g)
    rows = []
    for m in sorted(g, key=lambda m: (d[m], m)):
        ts_test = f"test/{m}.test.ts"
        rows.append({
            "module": m,
            "layer": d[m],
            "deps": g[m],
            "py": f"kestrel/{m}.py",
            "ts": f"ts/src/{m}.ts",
            "ts_test": f"ts/{ts_test}",
            "ported": (TS / "src" / f"{m}.ts").exists(),
            "ts_test_present": (TS / ts_test).exists(),
            "ts_tests_pass": None,
        })
    present = [r["ts_test"].removeprefix("ts/") for r in rows if r["ts_test_present"]]
    if run_tests and present:
        results = run_vitest(present)
        for r in rows:
            if r["ts_test_present"]:
                key = r["ts_test"].removeprefix("ts/")
                r["ts_tests_pass"] = "unknown" if results is None or key not in results else results[key]
    return rows


def ready(rows: list[dict]) -> list[str]:
    """Modules not yet ported whose dependencies are all ported."""
    ported = {r["module"] for r in rows if r["ported"]}
    return [r["module"] for r in rows if not r["ported"] and all(dep in ported for dep in r["deps"])]


def cell(key: str, value) -> str:
    if key == "layer":
        return f"L{value}"
    return {True: "yes", False: "no", None: "-"}.get(value, str(value))


def table(rows: list[dict]) -> str:
    cols = [("module", "module"), ("layer", "layer"), ("py", "python"), ("ts", "ts port"),
            ("ts_test", "ts test"), ("ported", "ported"), ("ts_test_present", "test?"), ("ts_tests_pass", "passing")]
    data = [[cell(k, r[k]) for k, _ in cols] for r in rows]
    widths = [max(len(h), *(len(row[i]) for row in data)) for i, (_, h) in enumerate(cols)]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    lines = [fmt.format(*(h for _, h in cols)), fmt.format(*("-" * w for w in widths))]
    lines += [fmt.format(*row) for row in data]
    lines = [line.rstrip() for line in lines]
    ported = sum(r["ported"] for r in rows)
    lines.append(f"\n{ported}/{len(rows)} modules ported")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="print JSON instead of a table")
    parser.add_argument("--next", action="store_true", help="list modules ready to port")
    parser.add_argument("--no-run", action="store_true", help="do not run vitest")
    args = parser.parse_args(argv)
    rows = collect(run_tests=not (args.no_run or args.next))
    if args.next:
        print("\n".join(ready(rows)))
    elif args.json:
        print(json.dumps(rows, indent=2))
    else:
        print(table(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
