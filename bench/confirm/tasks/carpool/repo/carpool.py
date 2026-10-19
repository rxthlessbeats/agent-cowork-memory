"""The office carpool: who drove whom, and what riders owe their driver for fuel.

A ride is a dict like
    {"driver": "Ana", "riders": ["Ben", "Cy"], "day": date(2026, 10, 12), "metres": 23400, "fuel": 1860}
where metres is the distance driven and fuel what the driver spent on fuel for it, in cents.
"""

from datetime import date

RIDES = [
    {"driver": "Ana", "riders": ["Ben", "Cy"], "day": date(2026, 10, 12), "metres": 23400, "fuel": 1860},
    {"driver": "Dev", "riders": ["Ana"], "day": date(2026, 10, 13), "metres": 3100, "fuel": 290},
    {"driver": "Ben", "riders": ["Cy", "Dev", "Eli"], "day": date(2026, 10, 14), "metres": 61800, "fuel": 4950},
]


def riders_of(rides, driver):
    """Everyone who rode with driver, each name once, in alphabetical order."""
    return sorted({name for ride in rides if ride["driver"] == driver for name in ride["riders"]})
