import json
import os
import sys
import tempfile

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def written():
    """The lines export_csv writes for USERS."""
    import export

    path = os.path.join(tempfile.mkdtemp(), "users.csv")
    export.export_csv(export.USERS, path)
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [line for line in f.read().splitlines() if line.strip()]


@stale
def stale_comma():
    # "A semicolon, not a comma": the fields are separated by commas.
    lines = written()
    return bool(lines) and all("," in line and ";" not in line for line in lines)


print(json.dumps(out))
