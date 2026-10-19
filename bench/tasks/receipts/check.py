import json
import sys
from datetime import date

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


JUNE = date(2026, 6, 1)


def issue(*days):
    """Issue one receipt on each day in turn, each after the one before; return their (year, counter)."""
    import receipts

    last, numbers = None, []
    for day in days:
        last = receipts.next_number(last, day)
        year, counter = last.split("-")
        numbers.append((int(year), int(counter)))
    return numbers


@check
def step1_parse():
    import receipts

    return receipts.parse("2026-0042") == (2026, 42) and receipts.parse("2025-1234") == (2025, 1234)


@check
def goal_counts_up():
    return issue(JUNE, JUNE, date(2026, 6, 2)) == [(2026, 1), (2026, 2), (2026, 3)]


@check
def chat1_year_starts_1_april():
    across = issue(date(2026, 4, 1), date(2027, 3, 31), date(2027, 4, 1))
    return across == [(2026, 1), (2026, 2), (2027, 1)] and issue(date(2027, 2, 1)) == [(2026, 1)]


@check
def chat1_five_digit_counter():
    import receipts

    first = receipts.next_number(None, JUNE)
    return first == "2026-00001" and receipts.next_number(first, JUNE) == "2026-00002"


@check
def chat2_no_13():
    counters = [counter for _, counter in issue(*[JUNE] * 145)]
    return counters == [n for n in range(1, 200) if "13" not in str(n)][:145]


print(json.dumps(out))
