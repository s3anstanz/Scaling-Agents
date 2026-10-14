"""Simple edge detection on the gray version of an image."""

from kestrel.core.mathutil import clamp, clamp_byte
from kestrel.ops.grayscale import grayscale


def gradient(img):
    """Edge strength |dx| + |dy| per pixel, clamped to 0..255, as a gray image.

    dx compares the left and right neighbours, dy the ones above and below;
    neighbours past the border reuse the nearest edge pixel.
    """
    g = grayscale(img)
    w, h = g.width, g.height
    levels = [p[0] for p in g.pixels]

    def at(x: int, y: int) -> int:
        return levels[clamp(y, 0, h - 1) * w + clamp(x, 0, w - 1)]

    out = []
    for y in range(h):
        for x in range(w):
            m = clamp_byte(abs(at(x + 1, y) - at(x - 1, y)) + abs(at(x, y + 1) - at(x, y - 1)))
            out.append((m, m, m))
    return g.with_pixels(out)


def edge_mask(img, level: int):
    """White where gradient >= level, black elsewhere."""
    return img.with_pixels([(255, 255, 255) if p[0] >= level else (0, 0, 0) for p in gradient(img).pixels])


def edge_count(img, level: int) -> int:
    """Number of pixels whose gradient is >= level."""
    return sum(1 for p in gradient(img).pixels if p[0] >= level)
