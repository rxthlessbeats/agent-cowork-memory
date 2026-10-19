"""Names for export files."""

PREFIX = "orders"


def filename(fmt, day):
    """The export's file name: the prefix, the day and the format, like "orders-2026-03-04.csv"."""
    return f"{PREFIX}-{day:%Y-%m-%d}.{fmt}"
