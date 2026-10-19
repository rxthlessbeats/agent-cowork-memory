"""CSV: ";" between the columns, and a header row of their names first."""

import csv
import io

FIELDS = ["id", "customer", "total"]


def render(orders):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, FIELDS, delimiter=";", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(orders)
    return buf.getvalue()
