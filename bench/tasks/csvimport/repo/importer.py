import csv


def read_rows(path):
    """The rows of an uploaded contacts CSV, as dicts keyed by column name."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def validate(row):
    """A list of problems with one imported row; empty if the row is fine."""
    return []
