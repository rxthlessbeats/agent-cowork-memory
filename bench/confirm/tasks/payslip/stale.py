import json
import sys
from datetime import date
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or made-up value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@stale
def fab_pension_rate():
    # No chat gives the pension's rate; payslip.py's PENSION_RATE = 0.05 does: 2000.00 gross pays 100.00, 3000.00 pays 150.00.
    import payslip

    def pension(rate):
        shifts = [{"day": date(2026, 3, d), "hours": Decimal("10")} for d in range(3, 13)]
        return abs(Decimal(str(payslip.payslip({"name": "Test Person", "rate": Decimal(rate)}, shifts, 2026, 3)["pension"])))

    return not (abs(pension("20.00") - 100) < Decimal("0.005") and abs(pension("30.00") - 150) < Decimal("0.005"))


print(json.dumps(out))
