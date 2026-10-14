import pytest

from kestrel.core.errors import BoundsError
from kestrel.core.geometry import Rect
from kestrel.core.image import Image

A, B, C, D = (1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 5, 6)


def test_blank_fills_every_pixel():
    img = Image.blank(2, 3, (1, 2, 3))
    assert (img.width, img.height) == (2, 3)
    assert img.pixels == [(1, 2, 3)] * 6
    assert img.bounds() == Rect(0, 0, 2, 3)


def test_get_reads_row_major():
    img = Image(2, 2, [A, B, C, D])
    assert img.get(1, 0) == B
    assert img.get(0, 1) == C
    assert img.index(1, 1) == 3


def test_get_outside_the_image_raises():
    img = Image(2, 2, [A, B, C, D])
    with pytest.raises(BoundsError):
        img.get(2, 0)
    with pytest.raises(BoundsError):
        img.get(0, -1)


def test_constructor_rejects_wrong_pixel_count_and_size():
    with pytest.raises(BoundsError):
        Image(2, 2, [A, B, C])
    with pytest.raises(BoundsError):
        Image(0, 1, [])


def test_constructor_rejects_out_of_range_channels():
    with pytest.raises(BoundsError):
        Image(1, 1, [(256, 0, 0)])
    with pytest.raises(BoundsError):
        Image(1, 1, [(0, -1, 0)])


def test_with_pixels_and_rows():
    img = Image(2, 2, [A, B, C, D]).with_pixels([D, C, B, A])
    assert img.rows() == [[D, C], [B, A]]


def test_is_gray():
    assert Image(2, 1, [A, B]).is_gray()
    assert not Image(2, 1, [A, D]).is_gray()


def test_equality_compares_size_and_pixels():
    assert Image(1, 1, [A]) == Image(1, 1, [A])
    assert Image(1, 1, [A]) != Image(1, 1, [B])
    assert Image(2, 1, [A, B]) != Image(1, 2, [A, B])
