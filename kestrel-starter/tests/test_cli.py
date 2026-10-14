import os
import tempfile
from pathlib import Path

from kestrel.cli import decode, encode, main
from kestrel.core.image import Image

SAMPLES = Path(__file__).resolve().parents[1] / "samples"


def test_decode_detects_pgm_and_ppm():
    assert decode(b"P2\n1 1\n255\n7\n") == Image(1, 1, [(7, 7, 7)])
    assert decode(b"P3\n1 1\n255\n1 2 3\n") == Image(1, 1, [(1, 2, 3)])


def test_encode_follows_output_extension():
    img = Image(1, 1, [(7, 7, 7)])
    assert encode(img, "out.pgm") == b"P2\n1 1\n255\n7\n"
    assert encode(img, "OUT.PPM") == b"P3\n1 1\n255\n7 7 7\n"


def test_wrong_argument_count_returns_2():
    assert main([]) == 2
    assert main(["a.ppm", "b.ppm"]) == 2


def test_missing_input_returns_1():
    out = os.path.join(tempfile.mkdtemp(), "out.ppm")
    assert main([str(SAMPLES / "missing.ppm"), out, "gray"]) == 1


def test_bad_spec_returns_1_and_writes_nothing():
    out = os.path.join(tempfile.mkdtemp(), "out.ppm")
    assert main([str(SAMPLES / "tiny.ppm"), out, "gray|sharpen"]) == 1
    assert not os.path.exists(out)


def test_runs_a_pipeline_end_to_end():
    out = os.path.join(tempfile.mkdtemp(), "out.ppm")
    assert main([str(SAMPLES / "tiny.ppm"), out, "gray|threshold:128"]) == 0
    with open(out, "rb") as fh:
        assert fh.read() == b"P3\n2 2\n255\n0 0 0 255 255 255\n0 0 0 255 255 255\n"
