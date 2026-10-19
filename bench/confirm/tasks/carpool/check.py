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


WEDNESDAY = date(2026, 10, 14)


def ride(riders=("Ben",), day=WEDNESDAY, metres=30000, fuel=1000):
    return {"driver": "Ana", "riders": list(riders), "day": day, "metres": metres, "fuel": fuel}


def names(n):
    return [f"R{i}" for i in range(n)]


def owed(r):
    """{rider: cents} for each rider transfers(r) says owes something."""
    import carpool

    return {rider: cents for rider, cents, _ in list(carpool.transfers(r)) if cents}


@check
def step1_share():
    import carpool

    return (
        carpool.share(ride(riders=["Ben", "Cy"], fuel=1000)) == 333
        and carpool.share(ride(riders=["Ben"], fuel=1861)) == 930
        and carpool.share(ride(riders=["Ben", "Cy", "Di"], fuel=2400)) == 600
    )


@check
def goal_riders_chip_in():
    import carpool

    got = list(carpool.transfers(ride(riders=["Ben", "Cy"], fuel=1500)))  # a share of 5.00 each
    return sorted(t[0] for t in got) == ["Ben", "Cy"] and all(0 < t[1] <= 500 and t[2] >= WEDNESDAY for t in got)


@check
def chat_cap_9_26():
    # Shares of 9.25, 9.26 and 9.27, then random rides of 20 to 150 km with shares from 3.00 to 20.00:
    # far from any free distance or transfer minimum, so only the cap decides.
    rng = random.Random(926)
    rides = [ride(fuel=2 * share) for share in (925, 926, 927)]
    for _ in range(60):
        n = rng.randint(1, 4)
        fuel = rng.randint(300, 2000) * (n + 1) + rng.randint(0, n)
        rides.append(ride(riders=names(n), metres=rng.randint(20000, 150000), fuel=fuel))

    def expect(r):
        share = r["fuel"] // (len(r["riders"]) + 1)
        return {name: min(share, 926) for name in r["riders"]}

    return all(owed(r) == expect(r) for r in rides)


@check
def chat_free_under_4175_m():
    # 4174, 4175 and 4176 metres, then random distances up to 12 km, with shares from 3.00 to 9.00.
    rng = random.Random(4175)
    rides = [ride(metres=metres) for metres in (4174, 4175, 4176)]  # a share of 5.00
    for _ in range(60):
        n = rng.randint(1, 4)
        rides.append(ride(riders=names(n), metres=rng.randint(0, 12000), fuel=rng.randint(300, 900) * (n + 1)))

    def expect(r):
        share = r["fuel"] // (len(r["riders"]) + 1)
        return {} if r["metres"] < 4175 else {name: share for name in r["riders"]}

    return all(owed(r) == expect(r) for r in rides)


@check
def chat_due_first_tuesday():
    # Rides on a Monday, a Tuesday and a Wednesday, then on random days over four years.
    import carpool

    rng = random.Random(1)
    days = [date(2026, 10, 12), date(2026, 10, 13), date(2026, 10, 14)]
    days += [date(2025, 1, 1) + timedelta(days=rng.randint(0, 1460)) for _ in range(60)]

    def expect(day):
        ahead = (1 - day.weekday()) % 7 or 7  # Tuesday is weekday 1; a Tuesday's ride is due a week later
        return day + timedelta(days=ahead)

    for day in days:
        got = list(carpool.transfers(ride(riders=["Ben", "Cy"], day=day, fuel=1500)))
        if len(got) != 2 or any(t[2] != expect(day) for t in got):
            return False
    return True


print(json.dumps(out))
