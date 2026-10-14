"""PGM gray images: reads P2 (text) and P5 (binary), writes P2."""

from kestrel.core.errors import FormatError
from kestrel.core.image import Image

WHITESPACE = b" \t\r\n\v\f"
COMMENT = ord("#")


def read_tokens(data: bytes, count: int, start: int = 0) -> tuple[list[str], int]:
    """Read count whitespace-separated tokens, skipping "#" comments to end of line."""
    tokens, i, n = [], start, len(data)
    while len(tokens) < count:
        while i < n and (data[i] in WHITESPACE or data[i] == COMMENT):
            if data[i] == COMMENT:
                while i < n and data[i] not in b"\r\n":
                    i += 1
            else:
                i += 1
        if i >= n:
            raise FormatError(f"unexpected end of data after {len(tokens)} of {count} values")
        begin = i
        while i < n and data[i] not in WHITESPACE and data[i] != COMMENT:
            i += 1
        tokens.append(data[begin:i].decode("ascii", errors="replace"))
    return tokens, i


def to_int(token: str, lo: int, hi: int) -> int:
    """Parse a decimal token and check it lies in lo..hi."""
    if not token.isdigit():
        raise FormatError(f"expected a number, got '{token}'")
    value = int(token)
    if not lo <= value <= hi:
        raise FormatError(f"value {value} outside {lo}..{hi}")
    return value


def parse_pgm(data: bytes) -> Image:
    """Decode a P2 or P5 file with maxval 255 into an Image of gray pixels."""
    header, end = read_tokens(data, 4)
    magic = header[0]
    if magic not in ("P2", "P5"):
        raise FormatError(f"not a PGM file (magic '{magic}')")
    w, h = to_int(header[1], 1, 65535), to_int(header[2], 1, 65535)
    if to_int(header[3], 1, 65535) != 255:
        raise FormatError("only maxval 255 is supported")
    if magic == "P2":
        values = [to_int(t, 0, 255) for t in read_tokens(data, w * h, end)[0]]
    else:
        values = list(data[end + 1:end + 1 + w * h])
        if len(values) != w * h:
            raise FormatError("truncated P5 pixel data")
    return Image(w, h, [(v, v, v) for v in values])


def format_pgm(img: Image) -> bytes:
    """Encode a gray image as P2 text; raises FormatError if any pixel has colour."""
    if not img.is_gray():
        raise FormatError("PGM can only store gray images")
    lines = ["P2", f"{img.width} {img.height}", "255"]
    for row in img.rows():
        lines.append(" ".join(str(p[0]) for p in row))
    return ("\n".join(lines) + "\n").encode("ascii")


def load_pgm(path: str) -> Image:
    with open(path, "rb") as fh:
        return parse_pgm(fh.read())


def save_pgm(path: str, img: Image) -> None:
    with open(path, "wb") as fh:
        fh.write(format_pgm(img))
