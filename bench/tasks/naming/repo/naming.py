"""File names for the nightly exports to the shared drive."""
from datetime import date

CLIENTS = {42: "Acme Corp.", 7: "Smith & Jones", 1503: "North/West Ltd"}
REPORTS = ("sales", "stock", "returns")


def export_name(client_id, report, day):
    """The file name for one client's report on one day."""
    return f"{CLIENTS[client_id]} {report} {day.isoformat()}.csv"


if __name__ == "__main__":
    import sys

    print(export_name(int(sys.argv[1]), sys.argv[2], date.fromisoformat(sys.argv[3])))
