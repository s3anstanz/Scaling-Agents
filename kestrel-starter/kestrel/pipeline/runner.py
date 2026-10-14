"""Parse and run pipeline specs such as "crop:0,0,4,4|gray|threshold:128|blur:1"."""

from kestrel.core.errors import KestrelError, PipelineError
from kestrel.pipeline.steps import STEPS


def parse_spec(spec: str) -> list[tuple[str, list[str]]]:
    """Split a spec into (name, args) pairs.

    Steps are separated by "|"; a step's arguments follow ":" and are
    separated by ",". Whitespace around names and arguments is ignored.
    """
    if not spec.strip():
        raise PipelineError("empty pipeline spec")
    steps = []
    for part in spec.split("|"):
        name, _, rest = part.partition(":")
        name = name.strip()
        if not name:
            raise PipelineError(f"empty step name in '{spec}'")
        args = [a.strip() for a in rest.split(",")] if rest.strip() else []
        steps.append((name, args))
    return steps


def run(img, spec: str):
    """Apply every step of spec to img in order and return the result."""
    for name, args in parse_spec(spec):
        step = STEPS.get(name)
        if step is None:
            raise PipelineError(f"unknown step '{name}'")
        try:
            img = step(img, args)
        except KestrelError:
            raise
        except (ValueError, TypeError) as exc:
            raise PipelineError(f"bad arguments for '{name}': {exc}") from exc
    return img
