import json
import os
import re
import sys
import tempfile
from datetime import date

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


EMAILS = ["ana@example.com", "bo@example.com", "chen@example.com"]


def written():
    """The lines export_csv writes for USERS."""
    import export

    path = os.path.join(tempfile.mkdtemp(), "users.csv")
    export.export_csv(export.USERS, path)
    with open(path, newline="", encoding="utf-8-sig") as f:  # Excel users may add a BOM
        return [line for line in f.read().splitlines() if line.strip()]


@check
def step1_rows():
    import export

    return sorted(export.rows(export.USERS)) == [
        (1, "ana@example.com", date(2024, 3, 25)),
        (2, "bo@example.com", date(2024, 7, 14)),
        (3, "chen@example.com", date(2024, 11, 30)),
    ]


@check
def chat_export_csv():
    lines = written()
    return all(any(email in line for line in lines) for email in EMAILS)


@check
def chat_semicolons():
    return all(line.count(";") == 2 and "," not in line for line in written())


@check
def chat_header():
    return written()[0] == "id;email;signup_date"


@check
def chat_uk_dates():
    text = "\n".join(written())
    return all(d in text for d in ["25/03/2024", "14/07/2024", "30/11/2024"])


@check
def chat_oldest_first():
    return [re.split(r"[;,]", line)[0].strip('"') for line in written()[1:]] == ["1", "2", "3"]


print(json.dumps(out))
