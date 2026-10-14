#!/usr/bin/env bash
# Proves the starter still teaches what the course says it does:
#   a naive TypeScript port of core/mathutil (Math.round, Math.trunc) must FAIL scripts/verify.sh,
#   a correct port must PASS it, and a port with a trap test deleted must FAIL.
# Expects kestrel-starter/ts/node_modules to be installed (npm ci) before it runs.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
fixtures="$root/ci/trap-fixtures"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

run_case() {
  local label="$1" impl="$2" expect="$3" mutate="${4:-}"
  local dir="$work/$label"
  cp -R "$root/kestrel-starter" "$dir"
  mkdir -p "$dir/ts/src/core" "$dir/ts/test/core"
  cp "$fixtures/$impl/ts/src/core/mathutil.ts" "$dir/ts/src/core/mathutil.ts"
  cp "$fixtures/test/core/mathutil.test.ts" "$dir/ts/test/core/mathutil.test.ts"
  if [ -n "$mutate" ]; then
    python3 - "$dir/ts/test/core/mathutil.test.ts" "$mutate" <<'PY'
import re, sys
path, name = sys.argv[1], sys.argv[2]
src = open(path).read()
new = re.sub(r'\n  it\("' + name + r'".*?\n  }\);\n', "\n", src, flags=re.S)
assert new != src, f"test {name} not found"
open(path, "w").write(new)
PY
  fi
  set +e
  "$dir/scripts/verify.sh" core/mathutil >"$work/$label.log" 2>&1
  local rc=$?
  set -e
  if { [ "$expect" = pass ] && [ $rc -eq 0 ]; } || { [ "$expect" = fail ] && [ $rc -ne 0 ]; }; then
    echo "ok   $label: verify.sh exited $rc (expected $expect)"
  else
    echo "FAIL $label: verify.sh exited $rc but expected $expect"
    cat "$work/$label.log"
    return 1
  fi
}

status=0
run_case naive-port naive fail || status=1
run_case correct-port correct pass || status=1
run_case dropped-trap-test correct fail test_round_half_even_sends_halves_to_the_even_neighbour || status=1

if [ $status -eq 0 ]; then
  if grep -q "test_round_half_even_sends_halves_to_the_even_neighbour" "$work/naive-port.log" \
    && grep -q "test_floor_div_rounds_toward_negative_infinity" "$work/naive-port.log"; then
    echo "ok   naive port fails on both planted traps (T1 rounding, T2 floor division)"
  else
    echo "FAIL naive port did not fail on both trap tests"
    cat "$work/naive-port.log"
    status=1
  fi
fi
exit $status
