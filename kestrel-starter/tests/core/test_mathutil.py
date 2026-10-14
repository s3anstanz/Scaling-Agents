import pytest

from kestrel.core.mathutil import clamp, clamp_byte, floor_div, lerp, mean_int, round_half_even


def test_clamp_limits_both_ends():
    assert clamp(5, 0, 3) == 3
    assert clamp(-2, 0, 3) == 0
    assert clamp(2, 0, 3) == 2


def test_clamp_rejects_an_empty_range():
    with pytest.raises(ValueError):
        clamp(1, 5, 4)


def test_clamp_byte_limits_to_0_255():
    assert clamp_byte(300) == 255
    assert clamp_byte(-5) == 0
    assert clamp_byte(77) == 77


def test_round_half_even_sends_halves_to_the_even_neighbour():
    assert round_half_even(0.5) == 0
    assert round_half_even(1.5) == 2
    assert round_half_even(2.5) == 2
    assert round_half_even(3.5) == 4
    assert round_half_even(-2.5) == -2


def test_round_half_even_rounds_other_values_to_nearest():
    assert round_half_even(2.4) == 2
    assert round_half_even(2.6) == 3
    assert round_half_even(-2.6) == -3


def test_floor_div_rounds_toward_negative_infinity():
    assert floor_div(7, 2) == 3
    assert floor_div(-7, 2) == -4
    assert floor_div(7, -2) == -4
    assert floor_div(-1, 4) == -1


def test_floor_div_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        floor_div(1, 0)


def test_lerp_and_mean_int():
    assert lerp(10, 20, 0.25) == 12.5
    assert mean_int([1, 2, 3, 4]) == 2
    assert mean_int([3, 4]) == 4
