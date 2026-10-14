"""RGB colours. A colour is an (r, g, b) tuple of ints in 0..255."""

from kestrel.core.mathutil import clamp_byte, round_half_even

Color = tuple[int, int, int]

BLACK: Color = (0, 0, 0)
WHITE: Color = (255, 255, 255)


def rgb(r: int, g: int, b: int) -> Color:
    """Build a colour, clamping each channel to 0..255."""
    return (clamp_byte(r), clamp_byte(g), clamp_byte(b))


def gray(value: int) -> Color:
    """The gray colour whose three channels all equal value (clamped)."""
    v = clamp_byte(value)
    return (v, v, v)


def is_gray(c: Color) -> bool:
    """True when all three channels are equal."""
    return c[0] == c[1] == c[2]


def to_gray(c: Color) -> int:
    """Luma approximation (r + 2g + b) / 4, rounded half to even."""
    r, g, b = c
    return round_half_even((r + 2 * g + b) / 4)


def invert(c: Color) -> Color:
    """The photographic negative of c."""
    return (255 - c[0], 255 - c[1], 255 - c[2])


def blend(a: Color, b: Color, t: float) -> Color:
    """Mix a toward b by t in [0, 1]; each channel rounded half to even."""
    if not 0 <= t <= 1:
        raise ValueError(f"blend factor {t} outside [0, 1]")
    r, g, bl = (round_half_even(x + (y - x) * t) for x, y in zip(a, b, strict=True))
    return (r, g, bl)
