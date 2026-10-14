"""Rectangles on the integer pixel grid."""

from dataclasses import dataclass

from kestrel.core.errors import BoundsError
from kestrel.core.mathutil import floor_div


@dataclass(frozen=True)
class Rect:
    """An axis-aligned rectangle; (x, y) is its top-left pixel."""

    x: int
    y: int
    w: int
    h: int

    def __post_init__(self) -> None:
        if self.w < 0 or self.h < 0:
            raise BoundsError(f"negative size {self.w}x{self.h}")

    @property
    def right(self) -> int:
        """One past the last column."""
        return self.x + self.w

    @property
    def bottom(self) -> int:
        """One past the last row."""
        return self.y + self.h

    def area(self) -> int:
        return self.w * self.h


def contains(rect: Rect, x: int, y: int) -> bool:
    """True when pixel (x, y) lies inside rect."""
    return rect.x <= x < rect.right and rect.y <= y < rect.bottom


def intersect(a: Rect, b: Rect) -> Rect | None:
    """The overlap of a and b, or None when they share no pixel."""
    x, y = max(a.x, b.x), max(a.y, b.y)
    right, bottom = min(a.right, b.right), min(a.bottom, b.bottom)
    if right <= x or bottom <= y:
        return None
    return Rect(x, y, right - x, bottom - y)


def translate(rect: Rect, dx: int, dy: int) -> Rect:
    """rect moved by (dx, dy)."""
    return Rect(rect.x + dx, rect.y + dy, rect.w, rect.h)


def center(rect: Rect) -> tuple[int, int]:
    """Centre pixel of a non-empty rect; ties go up and left (toward negative infinity)."""
    if rect.area() == 0:
        raise BoundsError("empty rect has no centre")
    cx = floor_div(rect.x + rect.right - 1, 2)
    cy = floor_div(rect.y + rect.bottom - 1, 2)
    return (cx, cy)
