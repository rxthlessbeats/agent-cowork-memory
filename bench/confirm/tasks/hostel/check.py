import json
import random
import sys
from datetime import date, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


BED_RATE = 2600


@check
def step1_stay_dates():
    import hostel

    return hostel.stay_dates(date(2026, 10, 16), 3) == [date(2026, 10, 16), date(2026, 10, 17), date(2026, 10, 18)] and (
        hostel.stay_dates(date(2026, 12, 31), 2) == [date(2026, 12, 31), date(2027, 1, 1)]
    )


@check
def goal_prices_stay():
    import hostel

    # A Wednesday and a Thursday night, and some tax on a short stay.
    return hostel.bed_price(date(2026, 10, 14), 2) == 2 * BED_RATE and hostel.city_tax(2, 1) > 0


@check
def chat_tax_4_38():
    # Exactly 438 cents for one guest's night (not 437 or 439), then random stays of 1 to 3 nights for 1 to 8
    # guests: short enough for any cap on taxed nights.
    import hostel

    rng = random.Random(438)
    cases = [(1, 1), (1, 2), (2, 1)] + [(rng.randint(1, 3), rng.randint(1, 8)) for _ in range(60)]
    return all(hostel.city_tax(nights, guests) == 438 * nights * guests for nights, guests in cases)


@check
def chat_sunday_17_off():
    # A Saturday, a Sunday and a Monday night alone, then random stays of up to three weeks.
    import hostel

    rng = random.Random(17)
    saturday = date(2026, 10, 17)
    cases = [(saturday + timedelta(days=k), 1) for k in (0, 1, 2)]
    cases += [(date(2025, 1, 1) + timedelta(days=rng.randint(0, 1000)), rng.randint(1, 21)) for _ in range(60)]

    def expect(arrival, nights):
        days = [arrival + timedelta(days=i) for i in range(nights)]
        return sum(BED_RATE * 83 // 100 if day.weekday() == 6 else BED_RATE for day in days)

    return all(hostel.bed_price(arrival, nights) == expect(arrival, nights) for arrival, nights in cases)


@check
def changed_tax_free_from_45():
    # 44, 45 and 46 nights, then random stays of up to 120 nights: from 45 nights there's no city tax at all.
    # Only whether there's any tax counts here, not how much.
    import hostel

    rng = random.Random(45)
    cases = [(nights, 1) for nights in (44, 45, 46)] + [(rng.randint(1, 120), rng.randint(1, 8)) for _ in range(60)]
    return all((hostel.city_tax(nights, guests) == 0) == (nights >= 45) for nights, guests in cases)


print(json.dumps(out))
