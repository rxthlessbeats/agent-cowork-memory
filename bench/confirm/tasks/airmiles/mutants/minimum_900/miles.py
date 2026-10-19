"""Air miles for the loyalty programme. See README.md; its earning rules are last year's."""

from datetime import date

from settings import MAX_MILES

MINIMUM = 900  # what the partner airline gives, so members earn the same with either
BUSINESS_BONUS = 18  # percent more than economy
DOUBLE_DAY = 6  # Sunday, as date.weekday() counts: Sunday flights are the emptiest


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
