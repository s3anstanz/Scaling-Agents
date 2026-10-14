"""Nearest-neighbour resizing."""

from kestrel.core.errors import BoundsError
from kestrel.core.image import Image
from kestrel.core.mathutil import floor_div


def source_index(i: int, src: int, dst: int) -> int:
    """Source column (or row) sampled for destination column i."""
    return floor_div(i * src, dst)


def resize(img: Image, width: int, height: int) -> Image:
    """Resize to width x height by sampling the nearest source pixel."""
    if width < 1 or height < 1:
        raise BoundsError(f"cannot resize to {width}x{height}")
    pixels = [
        img.get(source_index(x, img.width, width), source_index(y, img.height, height))
        for y in range(height)
        for x in range(width)
    ]
    return Image(width, height, pixels)


def scale(img: Image, factor: int) -> Image:
    """Enlarge by a whole-number factor."""
    if factor < 1:
        raise BoundsError(f"scale factor must be at least 1, got {factor}")
    return resize(img, img.width * factor, img.height * factor)


def half(img: Image) -> Image:
    """Halve each side, rounding down, never below 1 pixel."""
    return resize(img, max(1, floor_div(img.width, 2)), max(1, floor_div(img.height, 2)))
