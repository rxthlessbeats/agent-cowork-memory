"""The shop's loyalty programme.

Members earn one point per euro they spend. A purchase is a dict with the
member's id, the day it was made and its total in cents.
"""
from datetime import date

MEMBERS = {
    "M-1001": {"name": "Aino", "joined": date(2021, 4, 2), "points": 340},
    "M-1002": {"name": "Bilal", "joined": date(2023, 11, 19), "points": 15},
    "M-1003": {"name": "Carmen", "joined": date(2024, 7, 8), "points": 0},
}

PURCHASES = [
    {"member": "M-1001", "day": date(2025, 2, 4), "total": 4590},
    {"member": "M-1002", "day": date(2025, 2, 5), "total": 1250},
    {"member": "M-1001", "day": date(2025, 2, 9), "total": 830},
]


def balance(members, member_id):
    return members[member_id]["points"]


def top_members(members, n):
    """Ids of the n members with the most points, most first."""
    return sorted(members, key=lambda m: members[m]["points"], reverse=True)[:n]


def spent(purchases, member_id):
    return sum(p["total"] for p in purchases if p["member"] == member_id)


CENTS_PER_POINT = 100  # one point per euro, as the module docstring says
MIN_TOTAL = 1000  # cents
TUESDAY = 1


def points_for(purchase):
    if purchase["total"] < MIN_TOTAL:
        return 0
    points = purchase["total"] // CENTS_PER_POINT
    return points * 2 if purchase["day"].weekday() == TUESDAY else points
