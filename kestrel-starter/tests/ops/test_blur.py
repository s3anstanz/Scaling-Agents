import pytest

from kestrel.core.color import gray
from kestrel.core.errors import BoundsError
from kestrel.core.image import Image
from kestrel.ops.blur import box_blur


def test_radius_zero_is_identity():
    img = Image(2, 1, [(1, 2, 3), (4, 5, 6)])
    assert box_blur(img, 0) == img


def test_blur_averages_neighbours_inside_the_image():
    img = Image(3, 1, [gray(0), gray(3), gray(6)])
    assert box_blur(img, 1).pixels == [gray(2), gray(3), gray(4)]


def test_blur_rounds_half_to_even():
    img = Image(2, 1, [gray(2), gray(3)])
    assert box_blur(img, 1).pixels == [gray(2), gray(2)]


def test_blur_spreads_a_single_bright_pixel():
    img = Image(3, 3, [gray(0)] * 4 + [gray(9)] + [gray(0)] * 4)
    assert box_blur(img, 1).pixels == [gray(v) for v in (2, 2, 2, 2, 1, 2, 2, 2, 2)]


def test_uniform_image_stays_uniform():
    img = Image(3, 2, [(7, 8, 9)] * 6)
    assert box_blur(img, 2) == img


def test_negative_radius_raises():
    with pytest.raises(BoundsError):
        box_blur(Image(1, 1, [gray(0)]), -1)
