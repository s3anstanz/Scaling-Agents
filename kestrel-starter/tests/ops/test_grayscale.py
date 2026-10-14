import pytest

from kestrel.core.errors import KestrelError
from kestrel.core.image import Image
from kestrel.ops.grayscale import channel, grayscale


def test_grayscale_converts_every_pixel():
    out = grayscale(Image(2, 1, [(0, 4, 0), (255, 255, 255)]))
    assert out.pixels == [(2, 2, 2), (255, 255, 255)]
    assert out.is_gray()


def test_grayscale_rounds_half_to_even():
    out = grayscale(Image(3, 1, [(10, 0, 0), (0, 1, 0), (6, 0, 0)]))
    assert out.pixels == [(2, 2, 2), (0, 0, 0), (2, 2, 2)]


def test_channel_extracts_one_channel_as_gray():
    img = Image(1, 1, [(1, 2, 3)])
    assert channel(img, "r").pixels == [(1, 1, 1)]
    assert channel(img, "g").pixels == [(2, 2, 2)]
    assert channel(img, "b").pixels == [(3, 3, 3)]


def test_unknown_channel_raises():
    with pytest.raises(KestrelError):
        channel(Image(1, 1, [(1, 2, 3)]), "a")
