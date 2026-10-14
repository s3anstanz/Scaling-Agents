from kestrel.core.color import gray
from kestrel.core.image import Image
from kestrel.analysis.edges import edge_count, edge_mask, gradient


def test_uniform_image_has_no_edges():
    assert gradient(Image(3, 2, [(40, 50, 60)] * 6)).pixels == [gray(0)] * 6


def test_vertical_edge():
    img = Image(3, 1, [gray(0), gray(0), gray(255)])
    assert gradient(img).pixels == [gray(0), gray(255), gray(255)]


def test_strength_is_clamped_to_255():
    img = Image(3, 3, [gray(v) for v in (0, 0, 0, 0, 0, 255, 0, 255, 255)])
    assert gradient(img).get(1, 1) == gray(255)


def test_gradient_works_on_rounded_gray_levels():
    img = Image(2, 1, [(10, 0, 0), (0, 0, 0)])
    assert gradient(img).pixels == [gray(2), gray(2)]


def test_edge_mask_and_count():
    img = Image(3, 1, [gray(0), gray(0), gray(255)])
    assert edge_mask(img, 128).pixels == [gray(0), gray(255), gray(255)]
    assert edge_count(img, 128) == 2
