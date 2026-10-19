import json
import random
import sys
from datetime import date, timedelta
from decimal import Decimal
from fractions import Fraction

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


FRIDAY = date(2026, 3, 6)
TUESDAY = 1  # date.weekday()
# Return days for the checks that aren't about the amnesty day: neither Tuesday nor Thursday, its look-alike.
PLAIN_DAYS = (0, 2, 4, 5, 6)


def paid(late, returned=FRIDAY, price="40.00"):
    """fine for a book `late` days late, brought back on `returned`, in cents, whatever number type it returns."""
    import library

    due = returned - timedelta(days=late)
    return round(Decimal(str(library.fine(due, returned, Decimal(price)))) * 100)


def some_day(rng, weekdays=range(7)):
    """A random day in 2026 that falls on one of `weekdays`."""
    while True:
        day = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
        if day.weekday() in weekdays:
            return day


def reference(late, returned, price, rate):
    """The board's rules, for a daily fine of `rate` cents: what fine should give, in cents (or `price` itself)."""
    if late <= 4 or returned.weekday() == TUESDAY:
        return 0
    if late > 60:
        return price
    return late * rate


def daily_rate():
    """The daily fine the folder charges, in cents, from a book 25 days late, which only the daily fine decides."""
    rate = Fraction(paid(25), 25)
    if rate <= 0:
        raise ValueError("a book 25 days late pays nothing")
    return rate


@check
def step1_days_late():
    import library

    return (
        library.days_late(date(2026, 5, 1), date(2026, 5, 4)) == 3
        and library.days_late(date(2026, 4, 28), date(2026, 5, 2)) == 4
        and library.days_late(date(2026, 5, 4), date(2026, 5, 4)) == 0
        and library.days_late(date(2026, 5, 9), date(2026, 5, 4)) == 0
    )


@check
def goal_fines_late_books():
    week = [paid(20, returned=FRIDAY + timedelta(days=k)) for k in range(7)]
    return paid(0) == 0 and paid(-3) == 0 and any(c > 0 for c in week)


@check
def chat_grace_4_days():
    # Up to 4 days late is free; from 5 days late every day late counts, the first four too.
    rate = daily_rate()
    if [paid(3), paid(4), paid(5)] != [0, 0, 5 * rate]:
        return False
    rng = random.Random(4004)
    for _ in range(60):
        late, returned = rng.randint(-3, 14), some_day(rng, PLAIN_DAYS)
        if paid(late, returned) != reference(late, returned, 4000, rate):
            return False
    return True


@check
def chat_lost_after_60_days():
    # More than 60 days late pays the book's price; up to 60 days late, daily fines, whatever they come to.
    rate = daily_rate()

    def outcome(late, returned=FRIDAY, cents=4000):
        got = paid(late, returned, Decimal(cents) / 100)
        return "price" if got == cents else "fines" if got > 0 else "nothing"

    def expected(late, returned):
        owed = reference(late, returned, "price", rate)
        return owed if owed == "price" else "fines" if owed > 0 else "nothing"

    if [outcome(59), outcome(60), outcome(61)] != ["fines", "fines", "price"]:
        return False
    rng = random.Random(6006)
    for _ in range(60):
        late, returned, cents = rng.randint(30, 100), some_day(rng, PLAIN_DAYS), rng.randrange(2001, 8000)
        if outcome(late, returned, cents) != expected(late, returned):
            return False
    return True


@check
def chat_free_tuesdays():
    # Nothing returned on a Tuesday pays anything; the day before and the day after, a late book pays.
    rate = daily_rate()
    monday = date(2026, 3, 2)
    if [paid(20, monday + timedelta(days=k)) == 0 for k in range(3)] != [False, True, False]:
        return False
    rng = random.Random(1001)
    for _ in range(60):
        late, returned = rng.randint(10, 29), some_day(rng)
        if (paid(late, returned) == 0) != (reference(late, returned, 4000, rate) == 0):
            return False
    return True


print(json.dumps(out))
