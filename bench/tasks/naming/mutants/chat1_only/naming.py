"""File names for the nightly exports to the shared drive."""
import re
from datetime import date

CLIENTS = {42: "Acme Corp.", 7: "Smith & Jones", 1503: "North/West Ltd"}
REPORTS = ("sales", "stock", "returns")


def export_name(client_id, report, day):
    """The file name for one client's report on one day, like sales.ACMECORP.02032026.csv."""
    if report not in REPORTS:
        raise ValueError(f"unknown report {report!r}, expected one of {REPORTS}")
    client = re.sub(r"[^A-Z0-9]", "", CLIENTS[client_id].upper())
    return f"{report}.{client}.{day:%d%m%Y}.csv"


if __name__ == "__main__":
    import sys

    print(export_name(int(sys.argv[1]), sys.argv[2], date.fromisoformat(sys.argv[3])))
