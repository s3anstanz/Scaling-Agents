import pytest

from kestrel.core.errors import BoundsError
from kestrel.core.image import Image
from kestrel.ops.invert import invert, solarize


def test_invert_flips_every_channel():
    assert invert(Image(1, 1, [(0, 128, 255)])).pixels == [(255, 127, 0)]


def test_invert_twice_is_identity():
    img = Image(2, 1, [(1, 2, 3), (200, 100, 50)])
    assert invert(invert(img)) == img


def test_solarize_inverts_channels_at_or_above_level():
    assert solarize(Image(1, 1, [(100, 128, 200)]), 128).pixels == [(100, 127, 55)]


def test_solarize_level_outside_0_255_raises():
    with pytest.raises(BoundsError):
        solarize(Image(1, 1, [(0, 0, 0)]), 300)
