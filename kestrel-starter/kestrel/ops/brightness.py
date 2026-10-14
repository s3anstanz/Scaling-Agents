"""Make an image lighter or darker."""

from kestrel.core.image import Image
from kestrel.core.mathutil import clamp_byte, round_half_even


def brightness(img: Image, delta: int) -> Image:
    """Add delta to every channel, clamping to 0..255."""
    return img.with_pixels([(clamp_byte(r + delta), clamp_byte(g + delta), clamp_byte(b + delta))
                            for r, g, b in img.pixels])


def gain(img: Image, factor: float) -> Image:
    """Multiply every channel by factor, rounding half to even, then clamp."""
    if factor < 0:
        raise ValueError(f"gain factor must not be negative, got {factor}")
    return img.with_pixels([
        (clamp_byte(round_half_even(r * factor)),
         clamp_byte(round_half_even(g * factor)),
         clamp_byte(round_half_even(b * factor)))
        for r, g, b in img.pixels
    ])
