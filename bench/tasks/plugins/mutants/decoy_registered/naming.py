"""Names for export files."""

PREFIX = "orders"


def filename(fmt, day):
    """("csv", 2026-03-04) -> "orders-2026-03-04.csv"."""
    return f"{PREFIX}-{day.isoformat()}.{fmt}"
