"""Integer helpers whose exact Python semantics every port must reproduce."""


def clamp(value: int, lo: int, hi: int) -> int:
    """Limit value to the closed range [lo, hi]."""
    if lo > hi:
        raise ValueError(f"empty range [{lo}, {hi}]")
    return max(lo, min(hi, value))


def clamp_byte(value: int) -> int:
    """Limit an int to a colour channel's range, 0..255."""
    return clamp(value, 0, 255)


def round_half_even(x: float) -> int:
    """Round to the nearest int; exact halves go to the even neighbour.

    round_half_even(2.5) == 2 and round_half_even(3.5) == 4.
    """
    return round(x)


def floor_div(a: int, b: int) -> int:
    """Integer division rounding toward negative infinity: floor_div(-7, 2) == -4."""
    if b == 0:
        raise ZeroDivisionError("floor_div by zero")
    return a // b


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation from a (t=0) to b (t=1)."""
    return a + (b - a) * t


def mean_int(values: list[int]) -> int:
    """Mean of a non-empty list of ints, rounded half to even."""
    if not values:
        raise ValueError("mean of an empty list")
    return round_half_even(sum(values) / len(values))
