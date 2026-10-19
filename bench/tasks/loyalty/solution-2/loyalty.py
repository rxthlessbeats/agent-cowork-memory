"""The shop's loyalty programme.

Members earn one point for every full 2.50 they spend; purchases under 10.00
earn nothing, and purchases made on a Tuesday earn double. A purchase is a dict
with the member's id, the day it was made and its total in cents.
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

POINT_PRICE = 250  # cents per point
SMALLEST_EARNING = 1000  # cents; a smaller purchase earns nothing
DOUBLE_DAY = 2  # isoweekday: Tuesday


def balance(members, member_id):
    return members[member_id]["points"]


def top_members(members, n):
    """Ids of the n members with the most points, most first."""
    return sorted(members, key=lambda m: members[m]["points"], reverse=True)[:n]


def spent(purchases, member_id):
    """The member's total spend in cents over all their purchases; 0 if they have none."""
    total = 0
    for purchase in purchases:
        if purchase["member"] == member_id:
            total += purchase["total"]
    return total


def points_for(purchase):
    """The whole points a purchase earns."""
    total = purchase["total"]
    if total < SMALLEST_EARNING:
        return 0
    full_steps, _ = divmod(total, POINT_PRICE)
    multiplier = 2 if purchase["day"].isoweekday() == DOUBLE_DAY else 1
    return full_steps * multiplier
