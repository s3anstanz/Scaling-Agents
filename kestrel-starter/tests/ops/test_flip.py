import pytest

from kestrel.core.errors import KestrelError
from kestrel.core.image import Image
from kestrel.ops.flip import flip, flip_h, flip_v

A, B, C, D = (1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4)


def test_flip_h_mirrors_each_row():
    assert flip_h(Image(2, 2, [A, B, C, D])).pixels == [B, A, D, C]


def test_flip_v_mirrors_the_rows():
    assert flip_v(Image(2, 2, [A, B, C, D])).pixels == [C, D, A, B]


def test_flip_by_axis_name():
    img = Image(3, 1, [A, B, C])
    assert flip(img, "h") == Image(3, 1, [C, B, A])
    assert flip(img, "v") == img


def test_flip_unknown_axis_raises():
    with pytest.raises(KestrelError):
        flip(Image(1, 1, [A]), "x")
