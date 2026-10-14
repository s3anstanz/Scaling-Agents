"""The registry of named pipeline steps.

Each step takes an Image and a list of string arguments and returns a new
Image. Bad argument counts or values raise ValueError.
"""

from kestrel.ops.blur import box_blur
from kestrel.ops.brightness import brightness
from kestrel.ops.contrast import contrast
from kestrel.ops.crop import crop
from kestrel.ops.flip import flip
from kestrel.ops.grayscale import grayscale
from kestrel.ops.histogram import equalize
from kestrel.ops.invert import invert
from kestrel.ops.pad import pad
from kestrel.ops.resize import resize
from kestrel.ops.rotate import rotate
from kestrel.ops.threshold import threshold


def expect(args: list[str], lo: int, hi: int) -> list[str]:
    """Check that between lo and hi arguments were given."""
    if not lo <= len(args) <= hi:
        want = str(lo) if lo == hi else f"{lo}-{hi}"
        raise ValueError(f"expected {want} arguments, got {len(args)}")
    return args


def ints(args: list[str], count: int) -> list[int]:
    """Exactly count integer arguments."""
    return [int(a) for a in expect(args, count, count)]


def no_args(op):
    """Adapt op(img) into a step that takes no arguments."""
    def step(img, args):
        expect(args, 0, 0)
        return op(img)
    return step


def int_args(op, count: int):
    """Adapt op(img, n1, ..., n_count) into a step taking count integer arguments."""
    def step(img, args):
        return op(img, *ints(args, count))
    return step


def contrast_step(img, args):
    return contrast(img, float(expect(args, 1, 1)[0]))


def flip_step(img, args):
    return flip(img, expect(args, 1, 1)[0])


def pad_step(img, args):
    """pad:n or pad:n,mode."""
    a = expect(args, 1, 2)
    return pad(img, int(a[0]), a[1] if len(a) == 2 else "constant")


STEPS = {
    "blur": int_args(box_blur, 1),
    "brightness": int_args(brightness, 1),
    "contrast": contrast_step,
    "crop": int_args(crop, 4),
    "equalize": no_args(equalize),
    "flip": flip_step,
    "gray": no_args(grayscale),
    "invert": no_args(invert),
    "pad": pad_step,
    "resize": int_args(resize, 2),
    "rotate": int_args(rotate, 1),
    "threshold": int_args(threshold, 1),
}


def step_names() -> list[str]:
    """All step names, sorted."""
    return sorted(STEPS)
