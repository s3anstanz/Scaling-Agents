"""Cut a rectangular region out of an image."""

from kestrel.core.errors import BoundsError
from kestrel.core.geometry import Rect, center, intersect
from kestrel.core.image import Image


def crop_rect(img: Image, rect: Rect) -> Image:
    """The pixels of img inside rect; rect must be non-empty and fully inside img."""
    if rect.area() == 0:
        raise BoundsError("crop region is empty")
    if intersect(rect, img.bounds()) != rect:
        raise BoundsError(f"crop {rect} exceeds {img.width}x{img.height} image")
    pixels = [img.get(x, y) for y in range(rect.y, rect.bottom) for x in range(rect.x, rect.right)]
    return Image(rect.w, rect.h, pixels)


def crop(img: Image, x: int, y: int, w: int, h: int) -> Image:
    """The w x h region whose top-left pixel is (x, y)."""
    return crop_rect(img, Rect(x, y, w, h))


def trim(img: Image, n: int) -> Image:
    """Remove n pixels from every edge."""
    return crop(img, n, n, img.width - 2 * n, img.height - 2 * n)


def crop_center(img: Image, w: int, h: int) -> Image:
    """The w x h region centred on the image centre (ties go up and left)."""
    cx, cy = center(img.bounds())
    tx, ty = center(Rect(0, 0, w, h))
    return crop(img, cx - tx, cy - ty, w, h)
