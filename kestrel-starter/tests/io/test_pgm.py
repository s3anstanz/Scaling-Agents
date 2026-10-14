from pathlib import Path

import pytest

from kestrel.core.errors import FormatError
from kestrel.core.image import Image
from kestrel.io.pgm import format_pgm, load_pgm, parse_pgm

SAMPLES = Path(__file__).resolve().parents[2] / "samples"


def test_parse_plain_p2_into_gray_pixels():
    assert parse_pgm(b"P2\n2 1\n255\n7 200\n") == Image(2, 1, [(7, 7, 7), (200, 200, 200)])


def test_parse_skips_comments_and_odd_whitespace():
    data = b"P2\t# gray\n 2\n\n1 # one row\r\n255 \n 0\t\t9"
    assert parse_pgm(data).pixels == [(0, 0, 0), (9, 9, 9)]


def test_parse_binary_p5():
    assert parse_pgm(b"P5\n3 1\n255\n" + bytes([0, 35, 10])).pixels == [(0, 0, 0), (35, 35, 35), (10, 10, 10)]


def test_format_writes_p2():
    img = Image(2, 2, [(1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4)])
    assert format_pgm(img) == b"P2\n2 2\n255\n1 2\n3 4\n"


def test_format_rejects_colour_pixels():
    with pytest.raises(FormatError):
        format_pgm(Image(1, 1, [(1, 2, 3)]))


def test_sample_file_round_trips():
    img = load_pgm(str(SAMPLES / "checker.pgm"))
    assert (img.width, img.height) == (4, 4)
    assert img.get(3, 3) == (255, 255, 255)
    assert parse_pgm(format_pgm(img)) == img


def test_malformed_files_raise_format_error():
    with pytest.raises(FormatError):
        parse_pgm(b"P3\n1 1\n255\n0 0 0\n")
    with pytest.raises(FormatError):
        parse_pgm(b"P2\n2 1\n255\n1\n")
    with pytest.raises(FormatError):
        parse_pgm(b"P5\n2 1\n255\n" + bytes([1]))
