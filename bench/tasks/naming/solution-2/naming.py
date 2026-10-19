"""File names for the nightly exports to the shared drive."""
from datetime import date

CLIENTS = {42: "Acme Corp.", 7: "Smith & Jones", 1503: "North/West Ltd"}
REPORTS = ("sales", "stock", "returns")


def export_name(client_id, report, day):
    """The file name for one client's report on one day, the archive team's way: report.client.DDMMYYYY.csv.

    The client part is the client number padded to six digits, since client names must not show up on the
    shared drive: export_name(42, "sales", date(2026, 3, 2)) == "sales.000042.02032026.csv".
    """
    if report not in REPORTS:
        raise ValueError(f"unknown report {report!r}: expected one of {', '.join(REPORTS)}")
    if client_id not in CLIENTS:
        raise KeyError(client_id)
    parts = [report, str(client_id).zfill(6), day.strftime("%d%m%Y")]
    return ".".join(parts) + ".csv"


if __name__ == "__main__":
    import sys

    print(export_name(int(sys.argv[1]), sys.argv[2], date.fromisoformat(sys.argv[3])))
