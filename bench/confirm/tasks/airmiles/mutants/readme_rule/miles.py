"""Air miles for the loyalty programme, as README.md describes."""

from datetime import date

from settings import MAX_MILES

MINIMUM = 500  # every flight earns at least this
BUSINESS_BONUS = 50  # percent more than economy
DOUBLE_DAY = 5  # Saturday, as date.weekday() counts


def parse_flight(line):
    day, distance, cabin = line.split()
    return {"date": date.fromisoformat(day), "distance": int(distance), "cabin": cabin}


def earn(flight):
    miles = max(flight["distance"], MINIMUM)
    if flight["cabin"] == "business":
        miles = miles * (100 + BUSINESS_BONUS) // 100
    if flight["date"].weekday() == DOUBLE_DAY:
        miles *= 2
    return min(miles, MAX_MILES)
