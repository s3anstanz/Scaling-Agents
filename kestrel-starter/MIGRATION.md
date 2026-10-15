# Migrating Kestrel from Python to TypeScript

The Python code and its tests are the specification. The TypeScript port must behave identically: same return values, same errors, same output bytes.

## File mapping

| Python | TypeScript |
|---|---|
| `kestrel/<path>.py` | `ts/src/<path>.ts` |
| `tests/<dir>/test_<name>.py` | `ts/test/<dir>/<name>.test.ts` |
| `tests/test_cli.py` | `ts/test/cli.test.ts` |

Examples: `kestrel/core/color.py` → `ts/src/core/color.ts`, tested by `ts/test/core/color.test.ts`. Imports between ported modules are relative and extensionless: `import { roundHalfEven } from "./mathutil";`, and from a test `import { toGray } from "../../src/core/color";`.

`ts/src/index.ts` is the barrel. Each ported module adds one line: `export * from "./core/color";`. When two modules export the same name (`invert` in `core/color` and `ops/invert`; `readTokens`, `toInt`, `WHITESPACE` and `COMMENT` in `io/ppm` and `io/pgm`), add an explicit re-export after the `export *` lines, such as `export { invert } from "./ops/invert";`. A script that generates the barrel must write these lines too. Check the barrel from the repo root with `npm --prefix ts run typecheck`; `scripts/verify.sh` runs the tests but does not type-check it.

## Public API

- Each module's TS file exports the same public API as the Python module: every public function, class and constant. Names starting with `_` stay private (not exported).
- Function and method names: snake_case → camelCase (`to_gray` → `toGray`, `floor_div` → `floorDiv`, `parse_ppm` → `parsePpm`, `with_pixels` → `withPixels`).
- Classes keep their names (`Image`, `Rect`). Constants keep UPPER_CASE names (`BLACK`, `WHITE`, `STEPS`, `MODES`).
- Parameters keep their order. Python default arguments become TS default parameters (`pad(img, n, mode = "constant", fill = BLACK)`).
- `@classmethod` → `static` method (`Image.blank`). `@property` → getter (`rect.right`). `__eq__` → `equals(other): boolean`. `__repr__` → `toString()`.
- Frozen dataclasses → classes with `readonly` fields set in the constructor, in the same field order (`new Rect(x, y, w, h)`).

## Types

- `int` and `float` → `number`. `str` → `string`. `bytes` → `Uint8Array`. `None` → `null`.
- Tuples → readonly arrays: a colour `(r, g, b)` is `readonly [number, number, number]` (type `Color`); `tuple[int, int]` is `readonly [number, number]`.
- `list[X]` → `X[]`; `dict[str, X]` → `Record<string, X>`.
- File paths stay `string`; file I/O uses `node:fs` (`readFileSync`, `writeFileSync`).

## Errors

- Kestrel's error classes become classes with the same names: `KestrelError extends Error`, and `FormatError`, `BoundsError`, `PipelineError` extend `KestrelError`. Set `this.name` to the class name so messages read the same.
- Python built-in errors raised by Kestrel code: `ValueError` and `ZeroDivisionError` → throw `RangeError`.
- Code that catches `ValueError` (the runner and the CLI) catches the TS equivalents: `KestrelError` and `RangeError`.

## Tests

- Port tests 1:1 to vitest: same cases, same inputs, same expected values. Do not drop, merge, weaken or add cases.
- Each `def test_x():` becomes `it("test_x", ...)` with the Python function name verbatim as the title, inside a `describe("<path>", ...)` block. `scripts/verify.sh` checks that every Python test name appears.
- `assert a == b` → `expect(a).toEqual(b)` for arrays, tuples and objects, `toBe` for numbers, strings and booleans.
- `pytest.raises(E)` → `expect(() => ...).toThrow(E)`.
- Paths to `samples/` are resolved from the test file. From `ts/test/<dir>/` that is `fileURLToPath(new URL("../../../samples/tiny.ppm", import.meta.url))`; from a test directly in `ts/test/` it is `"../../samples/..."`.

## Command line

`ts/src/cli.ts` exports `decode`, `encode` and `main(argv: string[]): number` like the Python module, and when run directly (`npx tsx src/cli.ts in out spec` from `ts/`) calls `main(process.argv.slice(2))` and exits with its return value. `scripts/difftest.py` runs it that way.

## Known traps

Agents append discovered Python-vs-TypeScript behaviour differences here, one bullet each: what differs, which module, and the fix.
