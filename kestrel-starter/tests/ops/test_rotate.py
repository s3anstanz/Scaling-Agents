from kestrel.core.image import Image
from kestrel.ops.rotate import normalize_turns, rotate, rotate90

A, B, C, D = (1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4)


def test_rotate90_turns_clockwise():
    assert rotate90(Image(2, 2, [A, B, C, D])).pixels == [C, A, D, B]


def test_rotate90_swaps_width_and_height():
    out = rotate90(Image(3, 2, [A, B, C, D, A, B]))
    assert (out.width, out.height) == (2, 3)
    assert out.pixels == [D, A, A, B, B, C]


def test_zero_and_full_turns_are_identity():
    img = Image(2, 2, [A, B, C, D])
    assert rotate(img, 0) == img
    assert rotate(img, 4) == img


def test_normalize_turns_handles_negative_turns():
    assert normalize_turns(-1) == 3
    assert normalize_turns(-4) == 0
    assert normalize_turns(-5) == 3
    assert normalize_turns(6) == 2


def test_negative_turn_rotates_anticlockwise():
    img = Image(2, 2, [A, B, C, D])
    assert rotate(img, -1).pixels == [B, D, A, C]
    assert rotate(img, -1) == rotate(img, 3)
