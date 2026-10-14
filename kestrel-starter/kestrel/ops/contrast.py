"""Contrast adjustment and auto-stretch."""

from kestrel.core.errors import BoundsError
from kestrel.core.image import Image
from kestrel.core.mathutil import clamp_byte, floor_div, round_half_even


def _adjust(v: int, factor: float) -> int:
    return clamp_byte(round_half_even((v - 128) * factor + 128))


def contrast(img: Image, factor: float) -> Image:
    """Scale each channel's distance from mid-gray (128) by factor."""
    if factor < 0:
        raise BoundsError(f"contrast factor must not be negative, got {factor}")
    return img.with_pixels([(_adjust(r, factor), _adjust(g, factor), _adjust(b, factor))
                            for r, g, b in img.pixels])


def stretch(img: Image) -> Image:
    """Map the darkest channel value to 0 and the brightest to 255, linearly."""
    values = [v for p in img.pixels for v in p]
    lo, hi = min(values), max(values)
    if lo == hi:
        return img.with_pixels(img.pixels)

    def s(v: int) -> int:
        return floor_div((v - lo) * 255, hi - lo)

    return img.with_pixels([(s(r), s(g), s(b)) for r, g, b in img.pixels])
