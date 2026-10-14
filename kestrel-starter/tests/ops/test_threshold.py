import pytest

from kestrel.core.errors import BoundsError
from kestrel.core.image import Image
from kestrel.ops.threshold import fraction_above, threshold

BLACK, WHITE = (0, 0, 0), (255, 255, 255)


def test_threshold_splits_at_level():
    img = Image(3, 1, [(127, 127, 127), (128, 128, 128), (0, 255, 0)])
    assert threshold(img, 128).pixels == [BLACK, WHITE, WHITE]


def test_threshold_uses_rounded_gray_level():
    assert threshold(Image(1, 1, [(10, 0, 0)]), 3).pixels == [BLACK]


def test_level_zero_makes_everything_white():
    assert threshold(Image(2, 1, [BLACK, (9, 9, 9)]), 0).pixels == [WHITE, WHITE]


def test_fraction_above():
    img = Image(4, 1, [BLACK, BLACK, BLACK, WHITE])
    assert fraction_above(img, 128) == 0.25


def test_level_outside_0_255_raises():
    with pytest.raises(BoundsError):
        threshold(Image(1, 1, [BLACK]), 256)
    with pytest.raises(BoundsError):
        fraction_above(Image(1, 1, [BLACK]), -1)
