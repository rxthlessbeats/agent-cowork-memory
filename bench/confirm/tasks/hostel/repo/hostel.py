"""The hostel's dorms and prices.

Prices are in cents. A stay starts on its arrival date and lasts some nights: arriving on Friday
16 October 2026 for 3 nights means the nights of the 16th, 17th and 18th.
"""

from datetime import date

BED_RATE = 2600  # one bed for one night
TAXED_NIGHTS = 10  # the city taxes at most this many nights of a stay

DORMS = {"Atlas": 8, "Birch": 6, "Cedar": 4}  # beds in each dorm


def beds():
    """How many beds the hostel has."""
    return sum(DORMS.values())
