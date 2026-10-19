import csv
from datetime import date
from operator import itemgetter

USERS = [
    {"id": 3, "email": "chen@example.com", "name": "Chen", "signup": date(2024, 11, 30)},
    {"id": 1, "email": "ana@example.com", "name": "Ana", "signup": date(2024, 3, 25)},
    {"id": 2, "email": "bo@example.com", "name": "Bo", "signup": date(2024, 7, 14)},
]


def rows(users):
    return list(map(itemgetter("id", "email", "signup"), users))


def export_csv(users, path):
    """The users for finance, who open it in Excel in the UK: semicolons, DD/MM/YYYY, oldest signup first."""
    lines = [(id_, email, f"{signup:%d/%m/%Y}") for id_, email, signup in sorted(rows(users), key=itemgetter(2))]
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f, delimiter=";").writerows([("id", "email", "signup_date"), *lines])
