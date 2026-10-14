"""The Image type: width, height and a flat, row-major list of RGB pixels."""

from kestrel.core.color import BLACK, Color, is_gray, rgb
from kestrel.core.errors import BoundsError
from kestrel.core.geometry import Rect, contains


class Image:
    """A width x height grid of (r, g, b) pixels; pixel (x, y) is pixels[y * width + x]."""

    def __init__(self, width: int, height: int, pixels: list[Color]) -> None:
        if width < 1 or height < 1:
            raise BoundsError(f"image size must be at least 1x1, got {width}x{height}")
        if len(pixels) != width * height:
            raise BoundsError(f"{width}x{height} image needs {width * height} pixels, got {len(pixels)}")
        for p in pixels:
            if len(p) != 3 or rgb(*p) != tuple(p):
                raise BoundsError(f"invalid pixel {p!r}")
        self.width = width
        self.height = height
        self.pixels: list[Color] = [tuple(p) for p in pixels]

    @classmethod
    def blank(cls, width: int, height: int, fill: Color = BLACK) -> "Image":
        """An image filled with one colour."""
        return cls(width, height, [fill] * (width * height))

    def bounds(self) -> Rect:
        return Rect(0, 0, self.width, self.height)

    def index(self, x: int, y: int) -> int:
        """Flat index of pixel (x, y); raises BoundsError outside the image."""
        if not contains(self.bounds(), x, y):
            raise BoundsError(f"pixel ({x}, {y}) outside {self.width}x{self.height} image")
        return y * self.width + x

    def get(self, x: int, y: int) -> Color:
        return self.pixels[self.index(x, y)]

    def with_pixels(self, pixels: list[Color]) -> "Image":
        """A new image of the same size with the given pixels."""
        return Image(self.width, self.height, pixels)

    def rows(self) -> list[list[Color]]:
        """Pixels grouped into rows, top to bottom."""
        w = self.width
        return [self.pixels[y * w:(y + 1) * w] for y in range(self.height)]

    def is_gray(self) -> bool:
        return all(is_gray(p) for p in self.pixels)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Image):
            return NotImplemented
        return (self.width, self.height, self.pixels) == (other.width, other.height, other.pixels)

    def __repr__(self) -> str:
        return f"Image({self.width}x{self.height})"
