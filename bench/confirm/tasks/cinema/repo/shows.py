"""This week's shows."""

from datetime import datetime

SHOWS = [
    {"id": "S101", "film": "The Long Tide", "screen": "standard", "start": datetime(2026, 11, 6, 18, 30)},
    {"id": "S102", "film": "The Long Tide", "screen": "imax", "start": datetime(2026, 11, 6, 21, 0)},
    {"id": "S103", "film": "Paper Moons", "screen": "3d", "start": datetime(2026, 11, 7, 15, 45)},
    {"id": "S104", "film": "Paper Moons", "screen": "standard", "start": datetime(2026, 11, 7, 20, 15)},
]


def by_id(show_id):
    for show in SHOWS:
        if show["id"] == show_id:
            return show
    raise KeyError(show_id)
