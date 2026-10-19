"""Prints one day of the diary: python3 diary.py YYYY-MM-DD"""
import sys
from datetime import date, datetime

SESSIONS = [
    {"student": "ana", "tutor": "kim", "start": datetime(2026, 5, 4, 15, 0), "minutes": 45},
    {"student": "ben", "tutor": "lee", "start": datetime(2026, 5, 4, 16, 30), "minutes": 30},
    {"student": "ana", "tutor": "lee", "start": datetime(2026, 5, 7, 17, 0), "minutes": 60},
]


def day(sessions, on):
    """The sessions on the date `on`, earliest first."""
    return sorted((s for s in sessions if s["start"].date() == on), key=lambda s: s["start"])


if __name__ == "__main__":
    for s in day(SESSIONS, date.fromisoformat(sys.argv[1])):
        print(s["start"].strftime("%H:%M"), f"{s['minutes']} min", s["tutor"], s["student"])
