from kestrel.core.color import gray
from kestrel.core.image import Image
from kestrel.ops.histogram import cumulative, equalize, histogram


def test_histogram_counts_gray_levels():
    counts = histogram(Image(2, 2, [(0, 0, 0), (0, 0, 0), (255, 255, 255), (10, 0, 0)]))
    assert len(counts) == 256
    assert counts[0] == 2
    assert counts[2] == 1
    assert counts[255] == 1
    assert sum(counts) == 4


def test_cumulative_running_totals():
    assert cumulative([1, 0, 2]) == [1, 1, 3]


def test_equalize_spreads_levels_evenly():
    img = Image(4, 1, [gray(10), gray(20), gray(30), gray(40)])
    assert equalize(img).pixels == [gray(0), gray(85), gray(170), gray(255)]


def test_equalize_keeps_repeated_levels_together():
    img = Image(4, 1, [gray(0), gray(0), gray(128), gray(255)])
    assert equalize(img).pixels == [gray(0), gray(0), gray(128), gray(255)]


def test_equalize_single_level_returns_gray_version():
    assert equalize(Image(2, 1, [(10, 0, 0), (10, 0, 0)])).pixels == [gray(2), gray(2)]
