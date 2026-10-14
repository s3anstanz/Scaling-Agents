import pytest

from kestrel.core.color import gray
from kestrel.core.errors import BoundsError
from kestrel.core.image import Image
from kestrel.ops.crop import crop, crop_center, trim


def numbered(w, h):
    return Image(w, h, [gray(i) for i in range(w * h)])


def test_crop_returns_the_region():
    out = crop(numbered(3, 2), 1, 0, 2, 2)
    assert (out.width, out.height) == (2, 2)
    assert out.pixels == [gray(1), gray(2), gray(4), gray(5)]


def test_crop_outside_the_image_raises():
    with pytest.raises(BoundsError):
        crop(numbered(3, 2), 2, 0, 2, 1)
    with pytest.raises(BoundsError):
        crop(numbered(3, 2), -1, 0, 1, 1)


def test_empty_crop_raises():
    with pytest.raises(BoundsError):
        crop(numbered(3, 2), 0, 0, 0, 1)


def test_trim_removes_every_edge():
    assert trim(numbered(3, 3), 1).pixels == [gray(4)]


def test_crop_center_ties_go_up_and_left():
    assert crop_center(numbered(4, 4), 2, 2).pixels == [gray(5), gray(6), gray(9), gray(10)]
    assert crop_center(numbered(4, 4), 1, 1).pixels == [gray(5)]
