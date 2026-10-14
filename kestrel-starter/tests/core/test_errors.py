from kestrel.core.errors import BoundsError, FormatError, KestrelError, PipelineError, describe


def test_every_error_derives_from_kestrel_error():
    assert issubclass(FormatError, KestrelError)
    assert issubclass(BoundsError, KestrelError)
    assert issubclass(PipelineError, KestrelError)


def test_error_kinds_are_distinct():
    assert not issubclass(FormatError, BoundsError)
    assert not issubclass(BoundsError, PipelineError)
    assert not issubclass(PipelineError, FormatError)


def test_error_keeps_its_message():
    assert str(BoundsError("pixel (9, 9) outside 2x2 image")) == "pixel (9, 9) outside 2x2 image"


def test_describe_names_the_error_class():
    assert describe(FormatError("bad header")) == "FormatError: bad header"
    assert describe(PipelineError("unknown step 'x'")) == "PipelineError: unknown step 'x'"
