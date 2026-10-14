#!/usr/bin/env bash
# Definition of done for one module: its Python tests AND its ported TS tests pass.
#
#   scripts/verify.sh kestrel/core/color.py      (core/color also works)
#
# Exit 0 only if both suites pass and the TS test file contains every Python
# test name (tests port 1:1, see MIGRATION.md). Exit 1 otherwise, 2 on bad usage.
set -u
cd "$(dirname "$0")/.." || exit 2

if [ $# -ne 1 ]; then
  echo "usage: scripts/verify.sh kestrel/<package>/<module>.py" >&2
  exit 2
fi

mod="${1#./}"; mod="${mod#kestrel/}"; mod="${mod%.py}"
py_src="kestrel/$mod.py"
if [ ! -f "$py_src" ]; then
  echo "verify: no such module: $py_src" >&2
  exit 2
fi

dir="$(dirname "$mod")"; base="$(basename "$mod")"
if [ "$dir" = "." ]; then py_test="tests/test_$base.py"; else py_test="tests/$dir/test_$base.py"; fi
ts_src="ts/src/$mod.ts"
ts_test="ts/test/$mod.test.ts"
PY="${PYTHON:-python}"
command -v "$PY" >/dev/null 2>&1 || PY=python3

echo "== Python: $py_test"
"$PY" -m pytest -q "$py_test"
py_rc=$?

fail() { echo "FAIL $mod: $1" >&2; exit 1; }

[ -f "$ts_src" ] || fail "TS port missing: $ts_src (not ported yet)"
[ -f "$ts_test" ] || fail "TS test missing: $ts_test (port $py_test 1:1)"
[ -d ts/node_modules ] || fail "ts/node_modules missing: run (cd ts && npm ci)"

missing=""
for name in $(grep -oE '^def test_[A-Za-z0-9_]+' "$py_test" | cut -d' ' -f2); do
  grep -qE "[\"'\`]$name[\"'\`]" "$ts_test" || missing="$missing $name"
done
[ -z "$missing" ] || fail "TS test file lacks ported cases:$missing"

echo "== TypeScript: $ts_test"
(cd ts && npx vitest run "test/$mod.test.ts")
ts_rc=$?

[ "$py_rc" -eq 0 ] || fail "Python tests failed ($py_test)"
[ "$ts_rc" -eq 0 ] || fail "TS tests failed ($ts_test)"
echo "PASS $mod: Python and TypeScript tests pass"
