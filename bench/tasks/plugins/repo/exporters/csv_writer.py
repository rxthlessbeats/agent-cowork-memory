"""The CSV exporter: one row per order, its columns in COLUMNS order."""

import csv
import io

COLUMNS = ["id", "customer", "total"]


def render(orders, delimiter=",", header=False):
    """orders: a list of dicts with COLUMNS as keys. Returns the CSV text, with a header row first if asked."""
    out = io.StringIO()
    writer = csv.writer(out, delimiter=delimiter)
    if header:
        writer.writerow(COLUMNS)
    for order in orders:
        writer.writerow([order[column] for column in COLUMNS])
    return out.getvalue()
