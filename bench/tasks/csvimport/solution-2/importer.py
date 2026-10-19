import csv

NORDICS = ("SE", "NO", "DK", "FI")  # the only countries we ship to
MIN_AGE = 16  # legal's minimum


def read_rows(path):
    """The rows of an uploaded contacts CSV, as dicts keyed by column name."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        columns = [name.strip() for name in next(reader, [])]
        return [dict(zip(columns, (value.strip() for value in line))) for line in reader if line]


def validate(row):
    """A list of problems with one imported row; empty if the row is fine."""
    email, country, age = (row.get(column) or "" for column in ("email", "country", "age"))
    rules = [
        ("email", "@" in email[1:-1], "needs an @ with something on both sides"),
        ("country", country in NORDICS, f"must be one of {', '.join(NORDICS)}"),
        ("age", age.isdecimal() and int(age) >= MIN_AGE, f"must be {MIN_AGE} or older"),
    ]
    return [f"[{column}] {message}" for column, ok, message in rules if not ok]
