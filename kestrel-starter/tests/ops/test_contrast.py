import pytest

from kestrel.core.errors import BoundsError
from kestrel.core.image import Image
from kestrel.ops.contrast import contrast, stretch


def test_factor_one_is_identity_and_zero_is_flat_gray():
    img = Image(2, 1, [(0, 50, 255), (128, 129, 130)])
    assert contrast(img, 1) == img
    assert contrast(img, 0).pixels == [(128, 128, 128)] * 2


def test_factor_two_doubles_distance_from_mid_gray():
    assert contrast(Image(1, 1, [(100, 128, 200)]), 2).pixels == [(72, 128, 255)]


def test_contrast_rounds_half_to_even():
    assert contrast(Image(1, 1, [(129, 131, 133)]), 0.5).pixels == [(128, 130, 130)]


def test_negative_factor_raises():
    with pytest.raises(BoundsError):
        contrast(Image(1, 1, [(1, 1, 1)]), -0.5)


def test_stretch_maps_range_to_0_255_rounding_down():
    img = Image(3, 1, [(50, 50, 50), (100, 100, 100), (150, 150, 150)])
    assert stretch(img).pixels == [(0, 0, 0), (127, 127, 127), (255, 255, 255)]


def test_stretch_leaves_flat_image_unchanged():
    img = Image(2, 1, [(9, 9, 9), (9, 9, 9)])
    assert stretch(img) == img
