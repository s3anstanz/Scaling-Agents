"""Box blur."""

from kestrel.core.errors import BoundsError
from kestrel.core.image import Image
from kestrel.core.mathutil import round_half_even


def box_blur(img: Image, radius: int) -> Image:
    """Average each pixel with its neighbours within radius (a square window).

    Neighbours outside the image are skipped, so edge pixels average fewer
    values. Each channel mean is rounded half to even.
    """
    if radius < 0:
        raise BoundsError(f"blur radius must not be negative, got {radius}")
    w, h = img.width, img.height
    out = []
    for y in range(h):
        for x in range(w):
            sums = [0, 0, 0]
            count = 0
            for ny in range(max(0, y - radius), min(h, y + radius + 1)):
                for nx in range(max(0, x - radius), min(w, x + radius + 1)):
                    p = img.pixels[ny * w + nx]
                    sums[0] += p[0]
                    sums[1] += p[1]
                    sums[2] += p[2]
                    count += 1
            out.append((round_half_even(sums[0] / count),
                        round_half_even(sums[1] / count),
                        round_half_even(sums[2] / count)))
    return img.with_pixels(out)
