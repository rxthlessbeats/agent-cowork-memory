"""The hostel's dorms and prices.

Prices are in cents. A stay starts on its arrival date and lasts some nights: arriving on Friday
16 October 2026 for 3 nights means the nights of the 16th, 17th and 18th.
"""

from datetime import date, timedelta

BED_RATE = 2600  # one bed for one night
TAXED_NIGHTS = 10  # the city taxes at most this many nights of a stay

DORMS = {"Atlas": 8, "Birch": 6, "Cedar": 4}  # beds in each dorm


def beds():
    """How many beds the hostel has."""
    return sum(DORMS.values())


def stay_dates(arrival, nights):
    """Each night of a stay by its date: arriving on the 16th for 3 nights gives the 16th, 17th and 18th."""
    if nights < 0:
        raise ValueError("a stay can't have a negative number of nights")
    dates, night = [], arrival
    while len(dates) < nights:
        dates.append(night)
        night += timedelta(days=1)
    return dates


def bed_price(arrival, nights):
    """One bed for the stay, in cents: Sunday nights (Sunday to Monday, our emptiest) are 17% off."""
    sundays = sum(1 for night in stay_dates(arrival, nights) if night.isoweekday() == 7)
    return (nights - sundays) * BED_RATE + sundays * round(BED_RATE * 0.83)


def city_tax(nights, guests):
    """The city's tax for a booking, in cents: 4.38 per guest per night, for at most TAXED_NIGHTS nights.

    Stays of 45 nights or more pay none: the city counts those guests as residents.
    """
    taxed = 0 if nights >= 45 else min(nights, TAXED_NIGHTS)
    return round(4.38 * 100) * taxed * guests
