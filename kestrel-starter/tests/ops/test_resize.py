import pytest

from kestrel.core.errors import BoundsError
from kestrel.core.image import Image
from kestrel.ops.resize import half, resize, scale, source_index

A, B, C, D = (1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4)


def test_upscale_repeats_pixels():
    assert resize(Image(2, 1, [A, B]), 4, 1).pixels == [A, A, B, B]


def test_downscale_samples_every_other_pixel():
    assert resize(Image(4, 1, [A, B, C, D]), 2, 1).pixels == [A, C]


def test_non_integer_ratios_round_down():
    assert [source_index(i, 3, 5) for i in range(5)] == [0, 0, 1, 1, 2]
    assert resize(Image(3, 1, [A, B, C]), 2, 1).pixels == [A, B]


def test_scale_enlarges_by_whole_factor():
    out = scale(Image(1, 1, [A]), 3)
    assert (out.width, out.height) == (3, 3)
    assert out.pixels == [A] * 9


def test_half_never_goes_below_one_pixel():
    out = half(Image(5, 3, [A] * 15))
    assert (out.width, out.height) == (2, 1)
    assert half(Image(1, 1, [A])) == Image(1, 1, [A])


def test_invalid_sizes_raise():
    with pytest.raises(BoundsError):
        resize(Image(1, 1, [A]), 0, 1)
    with pytest.raises(BoundsError):
        scale(Image(1, 1, [A]), 0)
