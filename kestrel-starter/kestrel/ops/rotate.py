"""Rotate an image by quarter turns."""

from kestrel.core.image import Image
from kestrel.core.mathutil import floor_div


def normalize_turns(turns: int) -> int:
    """Map any number of clockwise quarter turns to 0..3; -1 becomes 3."""
    return turns - 4 * floor_div(turns, 4)


def rotate90(img: Image) -> Image:
    """Rotate one quarter turn clockwise; a w x h image becomes h x w."""
    w, h = img.width, img.height
    pixels = [img.get(ny, h - 1 - nx) for ny in range(w) for nx in range(h)]
    return Image(h, w, pixels)


def rotate(img: Image, turns: int) -> Image:
    """Rotate clockwise by turns quarter turns; negative turns rotate anticlockwise."""
    for _ in range(normalize_turns(turns)):
        img = rotate90(img)
    return img
