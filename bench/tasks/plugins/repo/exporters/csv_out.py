"""CSV."""

import csv
import io

FIELDS = ["id", "customer", "total"]


def render(orders):
    buf = io.StringIO()
    csv.writer(buf).writerows([order[f] for f in FIELDS] for order in orders)
    return buf.getvalue()
