"""The tip pool: the night's card tips, shared out among the staff who worked.

A shift is a dict like {"name": "Ana", "role": "floor", "start": "17:00", "end": "23:30", "trainee": False}:
role is "floor" or "kitchen", and start and end are "HH:MM" on the night's clock.
"""

TONIGHT = [
    {"name": "Ana", "role": "floor", "start": "17:00", "end": "23:30", "trainee": False},
    {"name": "Bo", "role": "floor", "start": "18:00", "end": "01:15", "trainee": True},
    {"name": "Cem", "role": "kitchen", "start": "15:30", "end": "22:45", "trainee": False},
    {"name": "Dita", "role": "kitchen", "start": "16:00", "end": "23:00", "trainee": False},
    {"name": "Eli", "role": "floor", "start": "20:00", "end": "21:00", "trainee": False},
]


def share_out(pool_cents, shifts, day):
    """Each person's share of the night's tip pool, in cents, as {name: cents}.

    pool_cents: the night's card tips; shifts: the night's shifts; day: the night's date (a datetime.date).
    """
    raise NotImplementedError


if __name__ == "__main__":
    from datetime import date

    print(share_out(41250, TONIGHT, date.today()))
