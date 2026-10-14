import pytest

from kestrel.core.color import blend, gray, invert, is_gray, rgb, to_gray


def test_rgb_clamps_each_channel():
    assert rgb(300, -4, 7) == (255, 0, 7)


def test_gray_repeats_the_clamped_value():
    assert gray(9) == (9, 9, 9)
    assert gray(300) == (255, 255, 255)


def test_to_gray_weights_green_twice():
    assert to_gray((0, 4, 0)) == 2
    assert to_gray((4, 0, 0)) == 1
    assert to_gray((255, 255, 255)) == 255


def test_to_gray_rounds_half_to_even():
    assert to_gray((10, 0, 0)) == 2
    assert to_gray((0, 1, 0)) == 0
    assert to_gray((6, 0, 0)) == 2
    assert to_gray((14, 0, 0)) == 4


def test_invert_and_is_gray():
    assert invert((0, 128, 255)) == (255, 127, 0)
    assert is_gray((3, 3, 3))
    assert not is_gray((3, 3, 4))


def test_blend_mixes_channels():
    assert blend((0, 0, 0), (10, 20, 30), 0.5) == (5, 10, 15)
    assert blend((0, 0, 0), (5, 7, 9), 0.5) == (2, 4, 4)
    assert blend((1, 2, 3), (9, 9, 9), 0) == (1, 2, 3)


def test_blend_rejects_factor_outside_0_1():
    with pytest.raises(ValueError):
        blend((0, 0, 0), (1, 1, 1), 1.5)
