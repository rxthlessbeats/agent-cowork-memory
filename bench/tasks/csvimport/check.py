import json
import os
import sys
import tempfile

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


ROW = {"name": "Ana", "email": "ana@example.com", "country": "SE", "age": "30"}


def problems(**changes):
    """validate() for ROW with these columns changed."""
    import importer

    return list(importer.validate({**ROW, **changes}))


@check
def step1_strips():
    import importer

    path = os.path.join(tempfile.mkdtemp(), "contacts.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write("name , email ,country, age\n Ana , ana@example.com ,SE, 30 \n")
    return importer.read_rows(path) == [ROW]


@check
def goal_bad_email():
    return problems() == [] and len(problems(email="not-an-email")) > 0


@check
def chat_nordic_only():
    return all(not problems(country=c) for c in ("SE", "NO", "DK", "FI")) and all(
        problems(country=c) for c in ("DE", "US")
    )


@check
def chat_min_age_16():
    return not problems(age="16") and problems(age="15")


@check
def chat_bracket_format():
    found = problems(email="not-an-email")
    return found and all(str(p).startswith("[email]") for p in found)


print(json.dumps(out))
