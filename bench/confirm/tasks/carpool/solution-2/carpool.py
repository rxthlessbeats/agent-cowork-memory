"""The office carpool: who drove whom, and what riders owe their driver for fuel.

A ride is a dict like
    {"driver": "Ana", "riders": ["Ben", "Cy"], "day": date(2026, 10, 12), "metres": 23400, "fuel": 1860}
where metres is the distance driven and fuel what the driver spent on fuel for it, in cents.
"""

from datetime import date, timedelta

import settings

RIDES = [
    {"driver": "Ana", "riders": ["Ben", "Cy"], "day": date(2026, 10, 12), "metres": 23400, "fuel": 1860},
    {"driver": "Dev", "riders": ["Ana"], "day": date(2026, 10, 13), "metres": 3100, "fuel": 290},
    {"driver": "Ben", "riders": ["Cy", "Dev", "Eli"], "day": date(2026, 10, 14), "metres": 61800, "fuel": 4950},
]

BUS_TICKET = 926  # cents: nobody pays more than this for one ride
STATION_HOP = 4175  # metres: shorter rides are free


def riders_of(rides, driver):
    """Everyone who rode with driver, each name once, in alphabetical order."""
    return sorted({name for ride in rides if ride["driver"] == driver for name in ride["riders"]})


def share(ride):
    """Each person's part of the fuel, the driver included, in whole cents rounded down: 1000 between 3 is 333."""
    people = 1 + len(ride["riders"])
    whole, _rest = divmod(ride["fuel"], people)
    return whole


def payday_after(day):
    """The first Tuesday after day; a Tuesday's next payday is a week later."""
    day += timedelta(days=1)
    while day.isoweekday() != 2:
        day += timedelta(days=1)
    return day


def transfers(ride):
    """What each rider sends the driver for ride: (rider, cents, due date), leaving out amounts not worth a transfer."""
    if ride["metres"] < STATION_HOP:
        return []
    cents = share(ride)
    if cents > BUS_TICKET:
        cents = BUS_TICKET
    due = payday_after(ride["day"])
    return [(rider, cents, due) for rider in ride["riders"] if cents >= settings.MIN_TRANSFER]
