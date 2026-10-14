import { describe, expect, it } from "vitest";
import { clamp, clampByte, floorDiv, lerp, meanInt, roundHalfEven } from "../../src/core/mathutil";

describe("core/mathutil", () => {
  it("test_clamp_limits_both_ends", () => {
    expect(clamp(5, 0, 3)).toBe(3);
    expect(clamp(-2, 0, 3)).toBe(0);
    expect(clamp(2, 0, 3)).toBe(2);
  });

  it("test_clamp_rejects_an_empty_range", () => {
    expect(() => clamp(1, 5, 4)).toThrow(RangeError);
  });

  it("test_clamp_byte_limits_to_0_255", () => {
    expect(clampByte(300)).toBe(255);
    expect(clampByte(-5)).toBe(0);
    expect(clampByte(77)).toBe(77);
  });

  it("test_round_half_even_sends_halves_to_the_even_neighbour", () => {
    expect(roundHalfEven(0.5)).toBe(0);
    expect(roundHalfEven(1.5)).toBe(2);
    expect(roundHalfEven(2.5)).toBe(2);
    expect(roundHalfEven(3.5)).toBe(4);
    expect(roundHalfEven(-2.5)).toBe(-2);
  });

  it("test_round_half_even_rounds_other_values_to_nearest", () => {
    expect(roundHalfEven(2.4)).toBe(2);
    expect(roundHalfEven(2.6)).toBe(3);
    expect(roundHalfEven(-2.6)).toBe(-3);
  });

  it("test_floor_div_rounds_toward_negative_infinity", () => {
    expect(floorDiv(7, 2)).toBe(3);
    expect(floorDiv(-7, 2)).toBe(-4);
    expect(floorDiv(7, -2)).toBe(-4);
    expect(floorDiv(-1, 4)).toBe(-1);
  });

  it("test_floor_div_by_zero_raises", () => {
    expect(() => floorDiv(1, 0)).toThrow(RangeError);
  });

  it("test_lerp_and_mean_int", () => {
    expect(lerp(10, 20, 0.25)).toBe(12.5);
    expect(meanInt([1, 2, 3, 4])).toBe(2);
    expect(meanInt([3, 4])).toBe(4);
  });
});
