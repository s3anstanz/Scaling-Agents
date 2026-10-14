"""Convert colour images to gray."""

from kestrel.core.color import gray, to_gray
from kestrel.core.errors import KestrelError
from kestrel.core.image import Image

CHANNELS = ("r", "g", "b")


def grayscale(img: Image) -> Image:
    """Replace every pixel with its gray level (see color.to_gray)."""
    return img.with_pixels([gray(to_gray(p)) for p in img.pixels])


def channel(img: Image, name: str) -> Image:
    """A gray image showing one channel: "r", "g" or "b"."""
    if name not in CHANNELS:
        raise KestrelError(f"unknown channel '{name}'")
    i = CHANNELS.index(name)
    return img.with_pixels([gray(p[i]) for p in img.pixels])
