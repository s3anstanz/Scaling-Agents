export function clamp(value: number, lo: number, hi: number): number {
  if (lo > hi) throw new RangeError(`empty range [${lo}, ${hi}]`);
  return Math.max(lo, Math.min(hi, value));
}

export function clampByte(value: number): number {
  return clamp(value, 0, 255);
}

export function roundHalfEven(x: number): number {
  const r = Math.abs(x % 1) === 0.5 ? 2 * Math.round(x / 2) : Math.round(x);
  return r === 0 ? 0 : r;
}

export function floorDiv(a: number, b: number): number {
  if (b === 0) throw new RangeError("floor_div by zero");
  return Math.floor(a / b);
}

export function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

export function meanInt(values: number[]): number {
  if (values.length === 0) throw new RangeError("mean of an empty list");
  return roundHalfEven(values.reduce((s, v) => s + v, 0) / values.length);
}
