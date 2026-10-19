"""The tip pool: the night's card tips, shared out among the staff who worked.

A shift is a dict like {"name": "Ana", "role": "floor", "start": "17:00", "end": "23:30", "trainee": False}:
role is "floor" or "kitchen", and start and end are "HH:MM" on the night's clock.
"""

from fractions import Fraction

from house import TRAINEE_SHARE

MIN_MINUTES = 77  # a shorter shift is someone covering a break, paid separately
SUNDAY = 6  # date.weekday(): the owner pays the kitchen a brunch bonus, so the floor gets the whole pool

TONIGHT = [
    {"name": "Ana", "role": "floor", "start": "17:00", "end": "23:30", "trainee": False},
    {"name": "Bo", "role": "floor", "start": "18:00", "end": "01:15", "trainee": True},
    {"name": "Cem", "role": "kitchen", "start": "15:30", "end": "22:45", "trainee": False},
    {"name": "Dita", "role": "kitchen", "start": "16:00", "end": "23:00", "trainee": False},
    {"name": "Eli", "role": "floor", "start": "20:00", "end": "21:00", "trainee": False},
]


def minutes(shift):
    """How many minutes a shift lasted; one that ends before it starts ran past midnight."""

    def clock(text):
        hours, mins = text.split(":")
        return int(hours) * 60 + int(mins)

    return (clock(shift["end"]) - clock(shift["start"])) % (24 * 60)


def share_out(pool_cents, shifts, day):
    """Each person's share of the night's tip pool, in cents, as {name: cents}.

    pool_cents: the night's card tips; shifts: the night's shifts; day: the night's date (a datetime.date).
    """
    # Everyone shares the pool by minutes worked; on Sundays only the floor does.
    roles = ("floor",) if day.weekday() == SUNDAY else ("floor", "kitchen")
    parts = {roles: Fraction(1)}
    shares = {shift["name"]: 0 for shift in shifts}
    for role, part in parts.items():
        team = [s for s in shifts if s["role"] in role and minutes(s) >= MIN_MINUTES]
        weights = {s["name"]: minutes(s) * (Fraction(TRAINEE_SHARE) if s.get("trainee") else 1) for s in team}
        total = sum(weights.values())
        if not total:
            continue
        exact = {name: pool_cents * part * weight / total for name, weight in weights.items()}
        whole = {name: int(x) for name, x in exact.items()}
        # Hand the cents lost to rounding down to the largest remainders, so the team's part adds up.
        left = round(pool_cents * part) - sum(whole.values())
        for name in sorted(exact, key=lambda n: exact[n] - whole[n], reverse=True)[:left]:
            whole[name] += 1
        shares.update(whole)
    return shares


if __name__ == "__main__":
    from datetime import date

    print(share_out(41250, TONIGHT, date.today()))
