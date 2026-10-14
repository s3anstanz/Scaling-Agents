import pytest

from kestrel.core.color import gray
from kestrel.core.image import Image
from kestrel.ops.crop import crop
from kestrel.ops.grayscale import grayscale
from kestrel.ops.pad import pad
from kestrel.pipeline.steps import STEPS, step_names

IMG = Image(4, 4, [gray(i * 10) for i in range(16)])


def test_registry_names():
    assert step_names() == [
        "blur", "brightness", "contrast", "crop", "equalize", "flip",
        "gray", "invert", "pad", "resize", "rotate", "threshold",
    ]


def test_steps_call_their_ops():
    color = Image(1, 1, [(10, 0, 0)])
    assert STEPS["gray"](color, []) == grayscale(color)
    assert STEPS["crop"](IMG, ["1", "1", "2", "2"]) == crop(IMG, 1, 1, 2, 2)


def test_pad_mode_is_optional():
    assert STEPS["pad"](IMG, ["1"]) == pad(IMG, 1)
    assert STEPS["pad"](IMG, ["1", "wrap"]) == pad(IMG, 1, "wrap")


def test_contrast_takes_a_decimal_factor():
    assert STEPS["contrast"](Image(1, 1, [(129, 131, 133)]), ["0.5"]).pixels == [(128, 130, 130)]


def test_wrong_argument_count_raises_value_error():
    with pytest.raises(ValueError):
        STEPS["blur"](IMG, [])
    with pytest.raises(ValueError):
        STEPS["gray"](IMG, ["1"])


def test_non_numeric_argument_raises_value_error():
    with pytest.raises(ValueError):
        STEPS["threshold"](IMG, ["abc"])
