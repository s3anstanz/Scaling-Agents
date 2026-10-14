#!/usr/bin/env python3
"""Kestrel's module dependency graph, derived from the import statements.

    python scripts/deps.py              adjacency JSON: {module: [modules it imports]}
    python scripts/deps.py --layers     topological waves: L0 has no deps, Ln depends only on earlier waves
    python scripts/deps.py --critical   the longest dependency chain (the critical path)
    python scripts/deps.py --dot        Graphviz source; edges point from a dependency to its dependent

Module ids are paths under kestrel/ without ".py": core/color, ops/blur, cli.
"""

import argparse
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "kestrel"


def module_ids() -> list[str]:
    """Every module id in kestrel/, sorted (package __init__ files excluded)."""
    return sorted(p.relative_to(PKG).with_suffix("").as_posix()
                  for p in PKG.rglob("*.py") if p.name != "__init__.py")


def imports_of(module: str, known: set[str]) -> list[str]:
    """Kestrel modules that module imports, found by parsing its source."""
    tree = ast.parse((PKG / f"{module}.py").read_text(encoding="utf-8"))
    found = set()
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names = [node.module] + [f"{node.module}.{alias.name}" for alias in node.names]
        for name in names:
            mid = name.removeprefix("kestrel.").replace(".", "/")
            if name.startswith("kestrel.") and mid in known and mid != module:
                found.add(mid)
    return sorted(found)


def graph() -> dict[str, list[str]]:
    """{module: sorted list of the modules it depends on}."""
    ids = module_ids()
    known = set(ids)
    return {m: imports_of(m, known) for m in ids}


def depths(g: dict[str, list[str]]) -> dict[str, int]:
    """Wave number of every module: 0 with no deps, else 1 + the deepest dep."""
    memo: dict[str, int] = {}

    def depth(m: str, trail: tuple[str, ...]) -> int:
        if m in trail:
            raise SystemExit(f"import cycle: {' -> '.join(trail + (m,))}")
        if m not in memo:
            memo[m] = 1 + max((depth(d, trail + (m,)) for d in g[m]), default=-1)
        return memo[m]

    for m in g:
        depth(m, ())
    return memo


def layers(g: dict[str, list[str]]) -> list[list[str]]:
    """Modules grouped by wave, each wave sorted."""
    d = depths(g)
    waves: list[list[str]] = [[] for _ in range(max(d.values()) + 1)]
    for m in sorted(g):
        waves[d[m]].append(m)
    return waves


def critical_path(g: dict[str, list[str]]) -> list[str]:
    """The longest chain of dependencies, from a wave-0 module to the deepest one.

    Ties are broken alphabetically, so the output is stable.
    """
    d = depths(g)
    node = min(m for m in g if d[m] == max(d.values()))
    path = [node]
    while g[node]:
        node = min(g[node], key=lambda m: (-d[m], m))
        path.append(node)
    return list(reversed(path))


def to_dot(g: dict[str, list[str]]) -> str:
    lines = ["digraph kestrel {", "  rankdir=LR;", "  node [shape=box, fontname=Helvetica];"]
    for i, wave in enumerate(layers(g)):
        members = " ".join(f'"{m}";' for m in wave)
        lines.append(f"  subgraph wave{i} {{ rank=same; {members} }}")
    for m, deps in g.items():
        lines.extend(f'  "{dep}" -> "{m}";' for dep in deps)
    lines.append("}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--layers", action="store_true", help="print topological waves")
    mode.add_argument("--critical", action="store_true", help="print the critical path")
    mode.add_argument("--dot", action="store_true", help="print Graphviz source")
    args = parser.parse_args(argv)
    g = graph()
    if args.layers:
        for i, wave in enumerate(layers(g)):
            print(f"L{i} ({len(wave)}): {', '.join(wave)}")
    elif args.critical:
        path = critical_path(g)
        print(f"{' -> '.join(path)}  ({len(path)} modules)")
    elif args.dot:
        print(to_dot(g))
    else:
        print(json.dumps(g, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
