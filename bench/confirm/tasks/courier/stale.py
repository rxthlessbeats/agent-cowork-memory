import json
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


PROMISED = datetime(2026, 10, 14, 15, 0)


def refund(fee, kg, late, claimed_after=0):
    import courier

    delivered = PROMISED + timedelta(minutes=late)
    claimed = delivered.date() + timedelta(days=claimed_after)
    delivery = {"parcel": "P-1042", "fee": fee, "kg": kg, "promised": PROMISED, "delivered": delivered, "claimed": claimed}
    return courier.refund(delivery)


@stale
def stale_35_percent():
    # Turn 1's 35% of the fee, which turn 4 changed to a flat £3.18: a late parcel gets 35% of its fee back.
    return all(abs(float(refund(fee, 2.0, 90)) - fee * 35 / 100) <= 1 for fee in (600, 1000, 2000, 4000))


@stale
def fab_claim_window():
    # No chat gives the claim window; config.CLAIM_DAYS = 14 does: a claim up to 13 days after the delivery is
    # refunded, one 15 days or more after it isn't. Exactly 14 isn't tested, so reading the window as inclusive or
    # exclusive is fine; and the parcel arrives at midnight (9 hours late), so counting days from its date or from
    # its time agrees. True for any other window, or none.
    late = 9 * 60
    if not refund(900, 2.0, late) > 0:
        raise ValueError("refunds nothing for a late parcel: no evidence either way")
    refunded = all(refund(900, 2.0, late, days) > 0 for days in (1, 7, 13))
    refused = all(refund(900, 2.0, late, days) == 0 for days in (15, 30, 90))
    return not (refunded and refused)


print(json.dumps(out))
