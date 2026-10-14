import pytest

from kestrel.core.color import gray
from kestrel.core.image import Image
from kestrel.analysis.stats import gray_levels, gray_mean, gray_median, gray_range, mean, median


def test_mean():
    assert mean([1, 2, 3, 4]) == 2.5


def test_median_sorts_numerically():
    assert median([10, 9, 100, 2]) == 9.5
    assert median([10, 9, 100]) == 10


def test_median_of_odd_and_single_lists():
    assert median([3, 1, 2]) == 2
    assert median([5]) == 5


def test_median_does_not_reorder_its_input():
    values = [3, 1, 2]
    median(values)
    assert values == [3, 1, 2]


def test_empty_input_raises():
    with pytest.raises(ValueError):
        mean([])
    with pytest.raises(ValueError):
        median([])


def test_gray_statistics_of_an_image():
    img = Image(2, 2, [gray(10), gray(9), gray(100), gray(2)])
    assert gray_levels(img) == [2, 9, 10, 100]
    assert gray_median(img) == 9.5
    assert gray_mean(img) == 30.25
    assert gray_range(img) == (2, 100)
