"""PPM colour images: reads P3 (text) and P6 (binary), writes P3."""

from kestrel.core.errors import FormatError
from kestrel.core.image import Image

WHITESPACE = b" \t\r\n\v\f"
COMMENT = ord("#")


def read_tokens(data: bytes, count: int, start: int = 0) -> tuple[list[str], int]:
    """Read count whitespace-separated tokens, skipping "#" comments to end of line.

    Returns the tokens and the offset just past the last one.
    """
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


def parse_ppm(data: bytes) -> Image:
    """Decode a P3 or P6 file with maxval 255."""
    header, end = read_tokens(data, 4)
    magic = header[0]
    if magic not in ("P3", "P6"):
        raise FormatError(f"not a PPM file (magic '{magic}')")
    w, h = to_int(header[1], 1, 65535), to_int(header[2], 1, 65535)
    if to_int(header[3], 1, 65535) != 255:
        raise FormatError("only maxval 255 is supported")
    if magic == "P3":
        values = [to_int(t, 0, 255) for t in read_tokens(data, 3 * w * h, end)[0]]
    else:
        body = data[end + 1:end + 1 + 3 * w * h]
        if len(body) != 3 * w * h:
            raise FormatError("truncated P6 pixel data")
        values = list(body)
    pixels = [(values[i], values[i + 1], values[i + 2]) for i in range(0, len(values), 3)]
    return Image(w, h, pixels)


def format_ppm(img: Image) -> bytes:
    """Encode as P3 text: a 3-line header, then one line per pixel row."""
    lines = ["P3", f"{img.width} {img.height}", "255"]
    for row in img.rows():
        lines.append(" ".join(f"{r} {g} {b}" for r, g, b in row))
    return ("\n".join(lines) + "\n").encode("ascii")


def load_ppm(path: str) -> Image:
    with open(path, "rb") as fh:
        return parse_ppm(fh.read())


def save_ppm(path: str, img: Image) -> None:
    with open(path, "wb") as fh:
        fh.write(format_ppm(img))
