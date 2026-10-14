"""Mirror an image horizontally or vertically."""

from kestrel.core.errors import KestrelError
from kestrel.core.image import Image


def flip_h(img: Image) -> Image:
    """Mirror left to right."""
    return img.with_pixels([p for row in img.rows() for p in reversed(row)])


def flip_v(img: Image) -> Image:
    """Mirror top to bottom."""
    return img.with_pixels([p for row in reversed(img.rows()) for p in row])


def flip(img: Image, axis: str) -> Image:
    """Flip along axis "h" (left-right) or "v" (top-bottom)."""
    if axis == "h":
        return flip_h(img)
    if axis == "v":
        return flip_v(img)
    raise KestrelError(f"unknown flip axis '{axis}', expected 'h' or 'v'")
