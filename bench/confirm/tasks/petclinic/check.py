import json
import random
import sys
from datetime import date, timedelta
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


TUESDAY = date(2026, 6, 2)  # 2 June 2026 is a Tuesday


def invoice(number, issued, balance="80.00"):
    return {"number": number, "owner": "Ana Lima", "pet": "Miso", "issued": issued, "balance": Decimal(balance)}


def chased(invoices, today):
    """The numbers of the invoices reminders(invoices, today) sends a letter for, in its order."""
    import billing

    return [number for number, _ in billing.reminders(invoices, today)]


def some_tuesday(rng):
    """One of eight Tuesdays: the day rule is chat_no_mondays's to test."""
    return TUESDAY + timedelta(weeks=rng.randint(0, 7))


@check
def step1_days_unpaid():
    import billing

    def refused(issued, today):
        try:
            billing.days_unpaid(invoice("S-3", issued), today)
        except ValueError:
            return True
        return False

    return (
        billing.days_unpaid(invoice("S-1", TUESDAY), TUESDAY) == 0
        and billing.days_unpaid(invoice("S-2", date(2025, 6, 2)), TUESDAY) == 365
        and refused(date(2026, 6, 3), TUESDAY)
    )


@check
def goal_reminders():
    # Whatever the rules: a big bill unpaid for 200 days is chased on a Tuesday, and one issued that day isn't.
    old = invoice("G-1", TUESDAY - timedelta(days=200))
    new = invoice("G-2", TUESDAY)
    return chased([new, old], TUESDAY) == ["G-1"]


@check
def chat_62_days():
    # Chased once unpaid for 62 days or more: 61 days isn't enough, 62 and 63 are (60, two round months, isn't).
    boundary = chased([invoice(f"D-{d}", TUESDAY - timedelta(days=d)) for d in (60, 61, 62, 63, 64)], TUESDAY)
    if boundary != ["D-62", "D-63", "D-64"]:
        return False

    def reference(invoices, today):
        return [i["number"] for i in invoices if (today - i["issued"]).days >= 62]

    rng = random.Random(62)
    for batch in range(8):
        today = some_tuesday(rng)
        invoices = [
            invoice(f"R-{batch}-{n}", today - timedelta(days=rng.choice([rng.randint(0, 400), rng.randint(55, 70)])), f"{rng.randint(10, 900)}.{rng.randint(0, 99):02d}")
            for n in range(10)
        ]
        if chased(invoices, today) != reference(invoices, today):
            return False
    return True


@check
def chat_1_61_minimum():
    # Balances under 1.61 aren't chased: 1.60 isn't, 1.61 and 1.62 are; nothing at all owed isn't either.
    old = TUESDAY - timedelta(days=100)
    boundary = chased([invoice(f"B-{b}", old, b) for b in ("0.00", "1.60", "1.61", "1.62")], TUESDAY)
    if boundary != ["B-1.61", "B-1.62"]:
        return False

    def reference(invoices):
        return [i["number"] for i in invoices if i["balance"] >= Decimal("1.61")]

    rng = random.Random(161)
    for batch in range(8):
        today = some_tuesday(rng)
        invoices = [
            invoice(f"M-{batch}-{n}", today - timedelta(days=rng.randint(90, 400)), f"{rng.choice([rng.randint(0, 400), rng.randint(150, 170)]) / 100:.2f}")
            for n in range(10)
        ]
        if chased(invoices, today) != reference(invoices):
            return False
    return True


@check
def chat_no_mondays():
    # No letters at all on a Monday; the Sunday before and the Tuesday after, the same invoices are chased.
    monday = TUESDAY - timedelta(days=1)
    invoices = [invoice("W-1", monday - timedelta(days=150)), invoice("W-2", monday - timedelta(days=300), "25.00")]
    boundary = (
        chased(invoices, monday - timedelta(days=1)) == ["W-1", "W-2"]
        and chased(invoices, monday) == []
        and chased(invoices, TUESDAY) == ["W-1", "W-2"]
    )
    if not boundary:
        return False

    def reference(invoices, today):
        return [] if today.weekday() == 0 else [i["number"] for i in invoices]

    rng = random.Random(1)
    for k in range(56):
        today = monday + timedelta(days=k)  # eight weeks, every day of the week
        invoices = [invoice(f"K-{k}-{n}", today - timedelta(days=rng.randint(90, 400)), f"{rng.randint(10, 900)}.00") for n in range(rng.randint(1, 4))]
        if chased(invoices, today) != reference(invoices, today):
            return False
    return True


print(json.dumps(out))
