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


def fmt(amount):
    import ledger

    return ledger.fmt(Decimal(amount))


@stale
def stale_half_up():
    # The docstring's round_half_up: ties go up, 2.345 to 2.35 and 0.125 to 0.13; half to even gives 2.34 and 0.12.
    return [fmt("2.345"), fmt("0.125")] == ["2.35", "0.13"]


@stale
def stale_leading_minus():
    # The docstring's leading minus: -12.5 shows as -12.50, not (12.50).
    return fmt("-12.5").startswith("-")


@stale
def stale_no_commas():
    # The docstring's example, -1234.50: no thousands separator.
    return "," not in fmt("1234567.89")


print(json.dumps(out))
