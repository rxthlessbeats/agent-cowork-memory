"""CSV, ";"-separated, with a header row."""

import csv
import io

FIELDS = ["id", "customer", "total"]


def render(orders):
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(FIELDS)
    writer.writerows([order[f] for f in FIELDS] for order in orders)
    return buf.getvalue()
