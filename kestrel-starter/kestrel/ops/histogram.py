"""Gray-level histograms and histogram equalisation."""

from kestrel.core.color import gray, to_gray
from kestrel.core.image import Image
from kestrel.core.mathutil import round_half_even


def histogram(img: Image) -> list[int]:
    """256 counts: how many pixels have each gray level."""
    counts = [0] * 256
    for p in img.pixels:
        counts[to_gray(p)] += 1
    return counts


def cumulative(counts: list[int]) -> list[int]:
    """Running totals of a histogram."""
    out, total = [], 0
    for c in counts:
        total += c
        out.append(total)
    return out


def equalize(img: Image) -> Image:
    """Spread gray levels so their cumulative distribution is roughly linear.

    The result is a gray image. An image with a single gray level is
    returned as its grayscale version unchanged.
    """
    cdf = cumulative(histogram(img))
    n = len(img.pixels)
    cdf_min = next(c for c in cdf if c > 0)
    levels = [to_gray(p) for p in img.pixels]
    if cdf_min == n:
        return img.with_pixels([gray(v) for v in levels])
    scale = 255 / (n - cdf_min)
    return img.with_pixels([gray(round_half_even((cdf[v] - cdf_min) * scale)) for v in levels])
