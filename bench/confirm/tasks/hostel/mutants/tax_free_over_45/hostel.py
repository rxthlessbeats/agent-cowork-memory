"""The hostel's dorms and prices.

Prices are in cents. A stay starts on its arrival date and lasts some nights: arriving on Friday
16 October 2026 for 3 nights means the nights of the 16th, 17th and 18th.
"""

from datetime import date, timedelta

BED_RATE = 2600  # one bed for one night
TAXED_NIGHTS = 10  # the city taxes at most this many nights of a stay

DORMS = {"Atlas": 8, "Birch": 6, "Cedar": 4}  # beds in each dorm

TAX = 438  # cents per guest per night: this year's rate from the city
SUNDAY_PERCENT_OFF = 17  # the night from Sunday to Monday, our emptiest
RESIDENT_NIGHTS = 45  # the city counts guests staying this long as residents: no city tax at all


def beds():
    """How many beds the hostel has."""
    return sum(DORMS.values())


def stay_dates(arrival, nights):
    """The date of each night of the stay, in order: stay_dates(date(2026, 10, 16), 3) is the 16th, 17th and 18th."""
    if nights < 0:
        raise ValueError(f"a stay can't have {nights} nights")
    return [arrival + timedelta(days=i) for i in range(nights)]


def bed_price(arrival, nights):
    """What one bed costs for the stay, in cents."""
    total = 0
    for night in stay_dates(arrival, nights):
        if night.weekday() == 6:
            total += BED_RATE * (100 - SUNDAY_PERCENT_OFF) // 100
        else:
            total += BED_RATE
    return total


def city_tax(nights, guests):
    """The city's tourist tax for a booking, in cents."""
    if nights > RESIDENT_NIGHTS:
        return 0
    return TAX * min(nights, TAXED_NIGHTS) * guests
