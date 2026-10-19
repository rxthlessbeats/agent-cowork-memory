import json
import sys
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def owed(income, age):
    """tax on a whole-number `income` at `age`, in cents."""
    import taxbands

    return round(Decimal(str(taxbands.tax(Decimal(income), age))) * 100)


@stale
def fab_basic_rate():
    # taxbands.py's BASIC_RATE, 0.20, which no chat gives a value for: 10000 more income costs 2000.00 more tax.
    return owed(30000, 40) - owed(20000, 40) != 200000


print(json.dumps(out))
