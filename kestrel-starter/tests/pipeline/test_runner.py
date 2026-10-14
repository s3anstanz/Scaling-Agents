import pytest

from kestrel.core.errors import BoundsError, PipelineError
from kestrel.core.image import Image
from kestrel.pipeline.runner import parse_spec, run

BLACK, WHITE = (0, 0, 0), (255, 255, 255)


def test_parse_spec_splits_steps_and_arguments():
    assert parse_spec("crop:0,0,4,4|gray|threshold:128|blur:1") == [
        ("crop", ["0", "0", "4", "4"]),
        ("gray", []),
        ("threshold", ["128"]),
        ("blur", ["1"]),
    ]


def test_parse_spec_ignores_surrounding_whitespace():
    assert parse_spec(" gray | pad: 1 , wrap ") == [("gray", []), ("pad", ["1", "wrap"])]


def test_empty_specs_and_steps_raise():
    with pytest.raises(PipelineError):
        parse_spec("  ")
    with pytest.raises(PipelineError):
        parse_spec("gray||invert")


def test_run_applies_steps_in_order():
    img = Image(2, 1, [(100, 100, 100), (200, 200, 200)])
    assert run(img, "gray|threshold:128").pixels == [BLACK, WHITE]
    assert run(img, "threshold:128|invert").pixels == [WHITE, BLACK]


def test_unknown_step_raises_pipeline_error():
    with pytest.raises(PipelineError):
        run(Image(1, 1, [BLACK]), "sharpen")


def test_bad_arguments_become_pipeline_errors():
    with pytest.raises(PipelineError):
        run(Image(1, 1, [BLACK]), "blur:x")


def test_kestrel_errors_from_ops_pass_through():
    with pytest.raises(BoundsError):
        run(Image(2, 2, [BLACK] * 4), "crop:0,0,9,9")
