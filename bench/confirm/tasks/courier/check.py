import json
import random
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


PROMISED = datetime(2026, 10, 14, 15, 0)


def refund(fee, kg, late, claimed_after=0):
    """What the folder refunds a delivery `late` minutes after its promised time, claimed days after it came."""
    import courier

    delivered = PROMISED + timedelta(minutes=late)
    claimed = delivered.date() + timedelta(days=claimed_after)
    delivery = {"parcel": "P-1042", "fee": fee, "kg": kg, "promised": PROMISED, "delivered": delivered, "claimed": claimed}
    return courier.refund(delivery)


def reference(fee, kg, late, claimed_after=0):
    """The chat's rules (a flat £3.18, as turn 4 changed it), with the repo's claim window (config.CLAIM_DAYS, 14)."""
    if claimed_after > 14 or kg > 20 or late <= 21:
        return 0
    return 318


@check
def step1_parse_scan():
    import courier

    return courier.parse_scan("P-1042 DELIVERED 2026-10-16T14:05") == (
        "P-1042",
        "DELIVERED",
        datetime(2026, 10, 16, 14, 5),
    ) and courier.parse_scan("P-2077 DELIVERED 2026-10-17T08:30") == ("P-2077", "DELIVERED", datetime(2026, 10, 17, 8, 30))


@check
def goal_refunds():
    # Whatever the rules: a light parcel on time gets nothing back, one three hours late gets something.
    return refund(900, 2.0, 0) == 0 and refund(900, 2.0, 180) > 0


@check
def chat_late_after_21_minutes():
    # Refunded or not, for light parcels claimed the same day: 20 and 21 minutes late not, 22 minutes late
    # refunded; and random lateness (whole minutes, early to two hours late), weights and fees.
    rng = random.Random(21)
    cases = [(900, 2.0, 20), (900, 2.0, 21), (900, 2.0, 22)]
    cases += [(rng.randrange(500, 5000, 10), rng.randint(1, 150) / 10, rng.randint(-60, 120)) for _ in range(60)]
    return all((refund(f, kg, late) > 0) == (reference(f, kg, late) > 0) for f, kg, late in cases)


@check
def changed_flat_318():
    # What a late, light parcel gets back, to the penny: a flat £3.18 (not £3.17 or £3.19), whatever its fee;
    # random fees, weights and lateness from an hour to ten hours.
    rng = random.Random(318)
    cases = [(500, 2.0, 60), (5000, 2.0, 600)]
    cases += [(rng.randrange(500, 5000), rng.randint(1, 150) / 10, rng.randint(60, 600)) for _ in range(60)]
    return all(refund(f, kg, late) == reference(f, kg, late) for f, kg, late in cases)


@check
def chat_no_refund_over_20kg():
    # Refunded or not, for parcels an hour and a half late: 19.9 and 20 kg refunded, 20.1 kg not; and random weights.
    rng = random.Random(20)
    cases = [19, 19.9, 20, 20.1, 21] + [rng.randint(1, 400) / 10 for _ in range(60)]
    return all((refund(900, kg, 90) > 0) == (reference(900, kg, 90) > 0) for kg in cases)


print(json.dumps(out))
