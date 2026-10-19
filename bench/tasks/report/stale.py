import json
import re
import subprocess
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


TOTALS = {"garden": 15000, "toys": 4599, "food": 2100, "books": 1550}


def run(*args):
    """What `report.py summary` prints."""
    p = subprocess.run([sys.executable, "report.py", "summary", *args], cwd=repo, capture_output=True, text=True, timeout=30)
    return p.stdout


@stale
def stale_prints_cents():
    # "The amounts are in cents, but print dollars": each category's line shows its total in cents (15000 for garden's
    # $150.00), whatever separates the name from the number (": ", ",", " $").
    shown = {}
    for line in run().splitlines():
        found = re.match(r"\s*(\w+)\W+?\$?\s*([\d,]*\d(\.\d+)?)\b", line)
        if found and found[1] in TOTALS:
            shown[found[1]] = float(found[2].replace(",", ""))
    return shown == {category: float(cents) for category, cents in TOTALS.items()}


print(json.dumps(out))
