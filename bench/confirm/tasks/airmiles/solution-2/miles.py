"""Air miles for the loyalty programme, by this year's rules (README.md still has last year's)."""

from datetime import datetime

import settings


def parse_flight(line):
    fields = line.split(" ")
    return {
        "date": datetime.strptime(fields[0], "%Y-%m-%d").date(),
        "distance": int(fields[1]),
        "cabin": fields[2],
    }


def earn(flight):
    earned = flight["distance"]
    if flight["cabin"] == "business":
        earned += earned * 18 / 100  # business: 18% more than economy
    earned = max(earned, 911)  # every flight earns at least 911
    if flight["date"].isoweekday() == 7:  # Sunday is the double-miles day
        earned *= 2
    return int(min(earned, settings.MAX_MILES))
