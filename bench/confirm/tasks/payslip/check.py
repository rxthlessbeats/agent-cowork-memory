import json
import random
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def slip(shifts, year=2026, month=3, rate="12.40"):
    """The payslip for (day, hours) shifts, at rate an hour."""
    import payslip

    employee = {"name": "Test Person", "rate": Decimal(rate)}
    return payslip.payslip(employee, [{"day": d, "hours": Decimal(h)} for d, h in shifts], year, month)


def mid_month(hours, year=2026, month=3):
    """Shifts of at most 10 hours from the 3rd of the month on, adding up to hours: inside any pay period."""
    hours, shifts, day = Decimal(hours), [], 3
    while hours > 0:
        shifts.append((date(year, month, day), str(min(hours, Decimal(10)))))
        hours -= 10
        day += 1
    return shifts


def num(x):
    return Decimal(str(x))


def day_of(x):
    return x.date() if isinstance(x, datetime) else x


def last_thursday(year, month):
    last = date(year + month // 12, month % 12 + 1, 1) - timedelta(days=1)
    return last - timedelta(days=(last.weekday() - 3) % 7)


@check
def step1_parse_shift():
    import payslip

    a = payslip.parse_shift("2026-03-05 7.5")
    b = payslip.parse_shift("  2026-12-31   8 ")
    return (
        a["day"] == date(2026, 3, 5)
        and num(a["hours"]) == Decimal("7.5")
        and b["day"] == date(2026, 12, 31)
        and num(b["hours"]) == 8
    )


@check
def goal_payslip():
    # Shifts in the middle of the month count whatever the pay period; net is gross less the pension; paid that month.
    s = slip([(date(2026, 3, d), "7.5") for d in range(9, 14)])
    paid = day_of(s["pay_date"])
    return (
        num(s["hours"]) == Decimal("37.5")
        and abs(num(s["gross"]) - Decimal("465.00")) < Decimal("0.005")
        and abs(num(s["net"]) - (num(s["gross"]) - abs(num(s["pension"])))) < Decimal("0.005")
        and (paid.year, paid.month) == (2026, 3)
    )


@check
def chat_period_23rd_to_22nd():
    # March 2026 runs from 23 February to 22 March: of 1, 2, 4, 8 and 16 hours on the 22nd and 23rd of February,
    # the 21st, 22nd and 23rd of March, only 2 + 4 + 8 count.
    marked = [(date(2026, 2, 22), "1"), (date(2026, 2, 23), "2"), (date(2026, 3, 21), "4"), (date(2026, 3, 22), "8")]
    edges = [num(slip([*marked, (date(2026, 3, 23), "16")])["hours"]) == 14]
    rng = random.Random(2201)
    same = []
    for _ in range(60):
        year, month = rng.randint(2024, 2031), rng.randint(1, 12)
        first = date(year, month, 1)
        shifts = [
            (first + timedelta(days=rng.randint(-45, 55)), str(Decimal(rng.randint(2, 20)) / 2))
            for _ in range(rng.randint(1, 8))
        ]
        start, end = (first - timedelta(days=1)).replace(day=23), first.replace(day=22)
        expected = sum((Decimal(h) for d, h in shifts if start <= d <= end), Decimal(0))
        same.append(num(slip(shifts, year, month)["hours"]) == expected)
    return all(edges) and all(same)


@check
def chat_pension_from_1561():
    def pays(hours, rate):
        return abs(num(slip(mid_month(hours), rate=rate)["pension"])) > 0

    # 100 hours at 15.60, 15.61 and 15.62 come to 1560.00, 1561.00 and 1562.00: only the first pays no pension.
    edges = [not pays("100", "15.60"), pays("100", "15.61"), pays("100", "15.62")]
    rng = random.Random(1561)
    same = []
    for _ in range(60):
        hours, rate = Decimal(rng.randint(800, 1300)) / 10, Decimal(rng.randint(110, 190)) / 10
        same.append(pays(hours, str(rate)) == (hours * rate >= 1561))
    return all(edges) and all(same)


@check
def chat_paid_last_thursday():
    def paid(year, month):
        return day_of(slip([(date(year, month, 10), "8")], year, month)["pay_date"])

    # April 2026 ends on a Thursday, July on a Friday and September on a Wednesday.
    edges = [paid(2026, 4) == date(2026, 4, 30), paid(2026, 7) == date(2026, 7, 30), paid(2026, 9) == date(2026, 9, 24)]
    rng = random.Random(4402)
    same = []
    for _ in range(60):
        year, month = rng.randint(2024, 2034), rng.randint(1, 12)
        same.append(paid(year, month) == last_thursday(year, month))
    return all(edges) and all(same)


print(json.dumps(out))
