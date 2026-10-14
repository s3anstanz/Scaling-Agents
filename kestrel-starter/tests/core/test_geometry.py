import pytest

from kestrel.core.errors import BoundsError
from kestrel.core.geometry import Rect, center, contains, intersect, translate


def test_rect_edges_and_area():
    r = Rect(2, 3, 4, 5)
    assert r.right == 6
    assert r.bottom == 8
    assert r.area() == 20


def test_negative_size_raises_bounds_error():
    with pytest.raises(BoundsError):
        Rect(0, 0, -1, 2)


def test_contains_is_half_open():
    r = Rect(0, 0, 2, 2)
    assert contains(r, 1, 1)
    assert not contains(r, 2, 0)
    assert not contains(r, -1, 0)


def test_intersect_returns_overlap_or_none():
    assert intersect(Rect(0, 0, 4, 4), Rect(2, 2, 4, 4)) == Rect(2, 2, 2, 2)
    assert intersect(Rect(0, 0, 2, 2), Rect(2, 0, 2, 2)) is None


def test_translate_moves_the_corner():
    assert translate(Rect(1, 1, 2, 2), -3, 4) == Rect(-2, 5, 2, 2)


def test_center_ties_go_up_and_left():
    assert center(Rect(0, 0, 3, 3)) == (1, 1)
    assert center(Rect(0, 0, 4, 4)) == (1, 1)


def test_center_with_negative_coordinates_floors():
    assert center(Rect(-4, -4, 2, 2)) == (-4, -4)
    assert center(Rect(-3, 0, 2, 1)) == (-3, 0)


def test_center_of_empty_rect_raises():
    with pytest.raises(BoundsError):
        center(Rect(0, 0, 0, 3))
