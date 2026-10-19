"""Ferry tickets."""

import fares
from harbour import BOARDING_MINUTES

CAR_LANE_UP_TO = 4631  # mm: the longest the bays on the car deck take; longer goes in the long lane
CHECK_IN_MINUTES = 64  # check-in closes this long before departure: the port's security screening
HARBOUR_FEE = 82  # cents a passenger, which the port charges us


def to_minutes(hhmm):
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def to_clock(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def ticket(booking):
    departs = to_minutes(booking["departure"])
    vehicle = booking["vehicle"]
    if vehicle is None:
        lane = None
    elif vehicle > CAR_LANE_UP_TO:
        lane = "long"
    else:
        lane = "car"
    price = booking["adults"] * (fares.ADULT + HARBOUR_FEE)
    price += {None: 0, "car": fares.CAR, "long": fares.LONG}[lane]
    return {
        "price": price,
        "lane": lane,
        "check_in": to_clock(departs - CHECK_IN_MINUTES),
        "boarding": to_clock(departs - BOARDING_MINUTES),
    }
