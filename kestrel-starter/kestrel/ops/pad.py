"""Add a border around an image."""

from kestrel.core.color import BLACK, Color
from kestrel.core.errors import BoundsError, KestrelError
from kestrel.core.image import Image

MODES = ("constant", "edge", "wrap")


def _source(i: int, size: int, mode: str) -> int | None:
    """Source index for padded coordinate i (already shifted by -n), or None for fill."""
    if 0 <= i < size:
        return i
    if mode == "edge":
        return 0 if i < 0 else size - 1
    if mode == "wrap":
        return i % size
    return None


def pad(img: Image, n: int, mode: str = "constant", fill: Color = BLACK) -> Image:
    """Grow the image by n pixels on every side.

    mode "constant" uses fill, "edge" repeats the nearest edge pixel and
    "wrap" tiles the image (the left border shows the right-hand columns).
    """
    if n < 0:
        raise BoundsError(f"pad width must not be negative, got {n}")
    if mode not in MODES:
        raise KestrelError(f"unknown pad mode '{mode}'")
    w, h = img.width + 2 * n, img.height + 2 * n
    pixels = []
    for y in range(h):
        sy = _source(y - n, img.height, mode)
        for x in range(w):
            sx = _source(x - n, img.width, mode)
            pixels.append(fill if sx is None or sy is None else img.get(sx, sy))
    return Image(w, h, pixels)
