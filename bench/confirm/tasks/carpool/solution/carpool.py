"""The office carpool: who drove whom, and what riders owe their driver for fuel.

A ride is a dict like
    {"driver": "Ana", "riders": ["Ben", "Cy"], "day": date(2026, 10, 12), "metres": 23400, "fuel": 1860}
where metres is the distance driven and fuel what the driver spent on fuel for it, in cents.
"""

from datetime import date, timedelta

from settings import MIN_TRANSFER

RIDES = [
    {"driver": "Ana", "riders": ["Ben", "Cy"], "day": date(2026, 10, 12), "metres": 23400, "fuel": 1860},
    {"driver": "Dev", "riders": ["Ana"], "day": date(2026, 10, 13), "metres": 3100, "fuel": 290},
    {"driver": "Ben", "riders": ["Cy", "Dev", "Eli"], "day": date(2026, 10, 14), "metres": 61800, "fuel": 4950},
]

CAP = 926  # cents: never more than the bus ticket
FREE_UNDER = 4175  # metres: the hop from the station to the office
PAYDAY = 1  # Tuesday, as date.weekday() counts


def riders_of(rides, driver):
    """Everyone who rode with driver, each name once, in alphabetical order."""
    return sorted({name for ride in rides if ride["driver"] == driver for name in ride["riders"]})


def share(ride):
    """The fuel cost split evenly between the driver and the riders, in whole cents, rounded down."""
    return ride["fuel"] // (len(ride["riders"]) + 1)


def transfers(ride):
    """A (rider, cents, due date) tuple for each rider who owes the driver money for the ride."""
    if ride["metres"] < FREE_UNDER:
        return []
    cents = min(share(ride), CAP)
    if cents < MIN_TRANSFER:
        return []
    due = ride["day"] + timedelta(days=(PAYDAY - ride["day"].weekday()) % 7 or 7)
    return [(rider, cents, due) for rider in ride["riders"]]
