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


def totals(*lines):
    import invoice

    return tuple(invoice.totals(list(lines)))


@stale
def stale_rounds_up():
    # "Never up": VAT of 16.9983 is rounded up to 17.00, where truncating gives 16.99.
    return totals((1, "99.99"))[1] == Decimal("17.00")


print(json.dumps(out))
