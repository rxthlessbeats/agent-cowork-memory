"""The tip pool: the night's card tips, shared out among the staff who worked.

A shift is a dict like {"name": "Ana", "role": "floor", "start": "17:00", "end": "23:30", "trainee": False}:
role is "floor" or "kitchen", and start and end are "HH:MM" on the night's clock.

Shared out as agreed at the staff meeting: the kitchen gets 38% and the floor the rest, each by minutes worked;
a shift under 77 minutes gets nothing and doesn't count; on Sundays the floor gets the whole pool.
"""

from datetime import datetime

import house

TONIGHT = [
    {"name": "Ana", "role": "floor", "start": "17:00", "end": "23:30", "trainee": False},
    {"name": "Bo", "role": "floor", "start": "18:00", "end": "01:15", "trainee": True},
    {"name": "Cem", "role": "kitchen", "start": "15:30", "end": "22:45", "trainee": False},
    {"name": "Dita", "role": "kitchen", "start": "16:00", "end": "23:00", "trainee": False},
    {"name": "Eli", "role": "floor", "start": "20:00", "end": "21:00", "trainee": False},
]


def minutes(shift):
    """How many minutes a shift lasted: 18:00 to 01:30 ran past midnight and lasted 450."""
    start = datetime.strptime(shift["start"], "%H:%M")
    end = datetime.strptime(shift["end"], "%H:%M")
    return int((end - start).total_seconds()) // 60 % 1440


def share_out(pool_cents, shifts, day):
    """Each person's share of the night's tip pool, in cents, as {name: cents}.

    pool_cents: the night's card tips; shifts: the night's shifts; day: the night's date (a datetime.date).
    """
    if day.isoweekday() == 7:
        pots = {"floor": pool_cents}
    else:
        kitchen = round(pool_cents * 0.38)
        pots = {"kitchen": kitchen, "floor": pool_cents - kitchen}
    result = dict.fromkeys((s["name"] for s in shifts), 0)
    for role, pot in pots.items():
        weight = {}
        for s in shifts:
            if s["role"] == role and minutes(s) >= 77:
                weight[s["name"]] = minutes(s) * (house.TRAINEE_SHARE if s.get("trainee") else 1.0)
        total = sum(weight.values())
        for name, w in weight.items():
            result[name] = round(pot * w / total)
    return result


if __name__ == "__main__":
    from datetime import date

    print(share_out(41250, TONIGHT, date.today()))
