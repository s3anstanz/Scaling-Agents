"""Command line entry point.

    python -m kestrel.cli <in.ppm|in.pgm> <out.ppm|out.pgm> "<spec>"

The input format is detected from the file's magic number; the output
format follows the output file's extension (.pgm writes PGM, anything else PPM).
Exit status: 0 on success, 1 on a Kestrel or file error, 2 on bad usage.
"""

import sys

from kestrel.io.pgm import format_pgm, parse_pgm
from kestrel.io.ppm import format_ppm, parse_ppm
from kestrel.pipeline.runner import run

USAGE = 'usage: python -m kestrel.cli <in.ppm|in.pgm> <out.ppm|out.pgm> "<spec>"'


def decode(data: bytes):
    """Parse PGM (P2/P5) or PPM (P3/P6) bytes."""
    return parse_pgm(data) if data[:2] in (b"P2", b"P5") else parse_ppm(data)


def encode(img, out_path: str) -> bytes:
    """Encode img in the format implied by out_path's extension."""
    return format_pgm(img) if out_path.lower().endswith(".pgm") else format_ppm(img)


def main(argv: list[str]) -> int:
    """Run one pipeline from argv = [input, output, spec]; return the exit status."""
    if len(argv) != 3:
        print(USAGE, file=sys.stderr)
        return 2
    src, dst, spec = argv
    try:
        with open(src, "rb") as fh:
            img = decode(fh.read())
        out = encode(run(img, spec), dst)
        with open(dst, "wb") as fh:
            fh.write(out)
    except (OSError, ValueError) as exc:
        print(f"kestrel: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
