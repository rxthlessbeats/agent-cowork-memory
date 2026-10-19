import csv


def read_rows(path):
    """The rows of an uploaded contacts CSV, as dicts keyed by column name."""
    with open(path, newline="", encoding="utf-8") as f:
        return [{k.strip(): v.strip() for k, v in row.items()} for row in csv.DictReader(f)]


def validate(row):
    """A list of problems with one imported row; empty if the row is fine."""
    problems = []
    user, _, domain = row.get("email", "").partition("@")
    if not user or not domain:
        problems.append("email: must look like name@domain")
    country = row.get("country", "")
    if len(country) != 2 or not country.isalpha():
        problems.append("country: must be a two-letter country code")
    if not row.get("age", "").isdigit():
        problems.append("age: must be a whole number")
    return problems
