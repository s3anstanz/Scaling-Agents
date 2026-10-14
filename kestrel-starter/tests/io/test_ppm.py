from pathlib import Path

import pytest

from kestrel.core.errors import FormatError
from kestrel.core.image import Image
from kestrel.io.ppm import format_ppm, load_ppm, parse_ppm

SAMPLES = Path(__file__).resolve().parents[2] / "samples"


def test_parse_plain_p3():
    img = parse_ppm(b"P3\n2 1\n255\n255 0 0 0 255 0\n")
    assert img == Image(2, 1, [(255, 0, 0), (0, 255, 0)])


def test_parse_skips_comments():
    data = b"P3\n# made by hand\n2 1\n# maxval next\n255\n255 0 0 # red\n0 255 0\n"
    assert parse_ppm(data) == Image(2, 1, [(255, 0, 0), (0, 255, 0)])


def test_parse_accepts_odd_whitespace():
    data = b"P3 2\t1\r\n\n  255\n255   0\t0\n\n0 255 0"
    assert parse_ppm(data) == Image(2, 1, [(255, 0, 0), (0, 255, 0)])


def test_comment_can_follow_a_token_directly():
    assert parse_ppm(b"P3\n2 1#size\n255\n1 2 3 4 5 6\n").pixels == [(1, 2, 3), (4, 5, 6)]


def test_parse_binary_p6_reads_raw_bytes():
    data = b"P6\n# binary\n2 1\n255\n" + bytes([35, 10, 32, 1, 2, 3])
    assert parse_ppm(data).pixels == [(35, 10, 32), (1, 2, 3)]


def test_format_writes_one_line_per_row():
    img = Image(2, 2, [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)])
    assert format_ppm(img) == b"P3\n2 2\n255\n1 2 3 4 5 6\n7 8 9 10 11 12\n"


def test_sample_files_round_trip():
    img = load_ppm(str(SAMPLES / "tiny.ppm"))
    assert img.pixels == [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]
    noisy = load_ppm(str(SAMPLES / "noisy.ppm"))
    assert (noisy.width, noisy.height) == (5, 5)
    assert parse_ppm(format_ppm(noisy)) == noisy


def test_malformed_files_raise_format_error():
    with pytest.raises(FormatError):
        parse_ppm(b"P2\n1 1\n255\n0\n")
    with pytest.raises(FormatError):
        parse_ppm(b"P3\n2 1\n255\n1 2 3\n")
    with pytest.raises(FormatError):
        parse_ppm(b"P3\n1 1\n15\n1 2 3\n")
    with pytest.raises(FormatError):
        parse_ppm(b"P3\n1 1\n255\n1 2 300\n")
