"""Summary statistics over numbers and over an image's gray levels."""

from kestrel.ops.histogram import histogram


def mean(values: list[float]) -> float:
    """Arithmetic mean of a non-empty list."""
    if not values:
        raise ValueError("mean of an empty list")
    return sum(values) / len(values)


def median(values: list[float]) -> float:
    """Middle value in numeric order; the mean of the two middle values for even lengths."""
    if not values:
        raise ValueError("median of an empty list")
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def gray_levels(img) -> list[int]:
    """Every pixel's gray level, in ascending order."""
    return [level for level, count in enumerate(histogram(img)) for _ in range(count)]


def gray_mean(img) -> float:
    return mean(gray_levels(img))


def gray_median(img) -> float:
    return median(gray_levels(img))


def gray_range(img) -> tuple[int, int]:
    """(darkest, brightest) gray level."""
    levels = gray_levels(img)
    return (levels[0], levels[-1])
