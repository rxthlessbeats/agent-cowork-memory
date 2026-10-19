import csv

COUNTRIES = {"SE", "NO", "DK", "FI"}
MIN_AGE = 16


def read_rows(path):
    """The rows of an uploaded contacts CSV, as dicts keyed by column name."""
    with open(path, newline="", encoding="utf-8") as f:
        return [{k.strip(): v.strip() for k, v in row.items()} for row in csv.DictReader(f)]


def validate(row):
    """A list of problems with one imported row; empty if the row is fine."""
    problems = []
    user, _, domain = row.get("email", "").partition("@")
    if not user or not domain:
        problems.append("[email] must look like name@domain")
    if row.get("country") not in COUNTRIES:
        problems.append("[country] must be one of SE, NO, DK, FI")
    age = row.get("age", "")
    if not age.isdigit() or int(age) <= MIN_AGE:
        problems.append(f"[age] must be over {MIN_AGE}")
    return problems
