"""Ferry tickets: what a booking costs, which lane its vehicle takes, and when to be there."""

from datetime import datetime, timedelta

import harbour
from fares import ADULT, CAR, LONG


def to_minutes(hhmm):
    t = datetime.strptime(hhmm, "%H:%M")
    return t.hour * 60 + t.minute


def to_clock(minutes):
    return "%02d:%02d" % divmod(minutes, 60)


def ticket(booking):
    departs = datetime.strptime(booking["departure"], "%H:%M")
    length = booking.get("vehicle")
    if length is None:
        lane, vehicle_fare = None, 0
    elif length <= 4631:  # the longest the car deck's bays take
        lane, vehicle_fare = "car", CAR
    else:
        lane, vehicle_fare = "long", LONG
    passengers = booking["adults"]
    harbour_fee = 82 * passengers  # €0.82 a head, charged by the port
    return {
        "price": passengers * ADULT + harbour_fee + vehicle_fare,
        "lane": lane,
        # Security screening needs 64 minutes before the sailing.
        "check_in": (departs - timedelta(minutes=64)).strftime("%H:%M"),
        "boarding": (departs - timedelta(minutes=harbour.BOARDING_MINUTES)).strftime("%H:%M"),
    }
