"""Exception hierarchy shared by every Kestrel module."""


class KestrelError(ValueError):
    """Base class for every error Kestrel raises on bad input."""


class FormatError(KestrelError):
    """An image file is malformed or uses an unsupported variant."""


class BoundsError(KestrelError):
    """A coordinate, size or region falls outside what is allowed."""


class PipelineError(KestrelError):
    """A pipeline spec names an unknown step or passes bad arguments."""


def describe(err: Exception) -> str:
    """Return "ErrorName: message" for display on the command line."""
    return f"{type(err).__name__}: {err}"
