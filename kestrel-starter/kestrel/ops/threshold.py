"""Turn an image into pure black and white."""

from kestrel.core.color import BLACK, WHITE, to_gray
from kestrel.core.errors import BoundsError
from kestrel.core.image import Image


def _check_level(level: int) -> None:
    if not 0 <= level <= 255:
        raise BoundsError(f"threshold level {level} outside 0..255")


def threshold(img: Image, level: int) -> Image:
    """White where the gray level is >= level, black elsewhere."""
    _check_level(level)
    return img.with_pixels([WHITE if to_gray(p) >= level else BLACK for p in img.pixels])


def fraction_above(img: Image, level: int) -> float:
    """Share of pixels whose gray level is >= level."""
    _check_level(level)
    hits = sum(1 for p in img.pixels if to_gray(p) >= level)
    return hits / len(img.pixels)
