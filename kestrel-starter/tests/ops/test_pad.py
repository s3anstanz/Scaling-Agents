import pytest

from kestrel.core.errors import BoundsError, KestrelError
from kestrel.core.image import Image
from kestrel.ops.pad import pad

K = (0, 0, 0)
A, B, C = (1, 1, 1), (2, 2, 2), (3, 3, 3)


def test_constant_pad_surrounds_with_black():
    out = pad(Image(1, 1, [A]), 1)
    assert (out.width, out.height) == (3, 3)
    assert out.pixels == [K, K, K, K, A, K, K, K, K]


def test_constant_pad_uses_fill_colour():
    out = pad(Image(1, 1, [A]), 1, "constant", (9, 9, 9))
    assert out.pixels.count((9, 9, 9)) == 8


def test_edge_pad_repeats_the_border():
    out = pad(Image(2, 1, [A, B]), 1, "edge")
    assert out.pixels == [A, A, B, B] * 3


def test_wrap_pad_tiles_from_the_opposite_side():
    out = pad(Image(3, 1, [A, B, C]), 1, "wrap")
    assert (out.width, out.height) == (5, 3)
    assert out.pixels == [C, A, B, C, A] * 3


def test_wrap_pad_wider_than_the_image():
    out = pad(Image(2, 1, [A, B]), 2, "wrap")
    assert out.rows()[0] == [A, B, A, B, A, B]


def test_zero_pad_is_identity():
    img = Image(2, 1, [A, B])
    assert pad(img, 0, "wrap") == img


def test_invalid_arguments_raise():
    with pytest.raises(BoundsError):
        pad(Image(1, 1, [A]), -1)
    with pytest.raises(KestrelError):
        pad(Image(1, 1, [A]), 1, "mirror")
