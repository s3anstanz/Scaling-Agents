import pytest

from kestrel.core.image import Image
from kestrel.ops.brightness import brightness, gain


def test_brightness_adds_and_clamps():
    assert brightness(Image(1, 1, [(250, 0, 100)]), 10).pixels == [(255, 10, 110)]


def test_negative_brightness_darkens_and_clamps():
    assert brightness(Image(1, 1, [(10, 30, 255)]), -20).pixels == [(0, 10, 235)]


def test_gain_rounds_half_to_even():
    assert gain(Image(1, 1, [(5, 7, 9)]), 0.5).pixels == [(2, 4, 4)]


def test_gain_clamps():
    assert gain(Image(1, 1, [(200, 1, 0)]), 2).pixels == [(255, 2, 0)]


def test_negative_gain_raises():
    with pytest.raises(ValueError):
        gain(Image(1, 1, [(1, 1, 1)]), -1)
