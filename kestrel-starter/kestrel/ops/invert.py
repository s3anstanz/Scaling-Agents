"""Photographic negatives."""

from kestrel.core.color import invert as invert_color
from kestrel.core.errors import BoundsError
from kestrel.core.image import Image


def invert(img: Image) -> Image:
    """Invert every channel of every pixel."""
    return img.with_pixels([invert_color(p) for p in img.pixels])


def solarize(img: Image, level: int) -> Image:
    """Invert only the channels whose value is >= level."""
    if not 0 <= level <= 255:
        raise BoundsError(f"solarize level {level} outside 0..255")
    pixels = []
    for p in img.pixels:
        r, g, b = (255 - v if v >= level else v for v in p)
        pixels.append((r, g, b))
    return img.with_pixels(pixels)
