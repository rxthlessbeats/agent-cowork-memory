import csv
from datetime import date

USERS = [
    {"id": 3, "email": "chen@example.com", "name": "Chen", "signup": date(2024, 11, 30)},
    {"id": 1, "email": "ana@example.com", "name": "Ana", "signup": date(2024, 3, 25)},
    {"id": 2, "email": "bo@example.com", "name": "Bo", "signup": date(2024, 7, 14)},
]


def rows(users):
    return [(u["id"], u["email"], u["signup"]) for u in users]


def export_csv(users, path):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["id", "email", "signup_date"])
        for id_, email, signup in sorted(rows(users), key=lambda r: r[2]):
            writer.writerow([id_, email, signup.strftime("%d/%m/%Y")])
