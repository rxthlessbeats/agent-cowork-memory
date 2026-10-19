"""Boarding at the dog kennel."""

from datetime import time
from decimal import ROUND_HALF_UP, Decimal

NIGHTLY = 3600  # cents a night for one dog
CHECKOUT = time(11, 0)  # dogs go home by 11:00 on their last day


def nights(checkin, collected):
    """Nights a stay covers, by date: checked in Monday 15:00 and collected Thursday 10:30 is 3."""
    return collected.toordinal() - checkin.toordinal()


def minutes_after_checkout(collected):
    """How many minutes after CHECKOUT on its own day `collected` is (negative before it)."""
    since_midnight = collected.hour * 60 + collected.minute + collected.second / 60
    return since_midnight - (CHECKOUT.hour * 60 + CHECKOUT.minute)


def bill(dogs, checkin, collected):
    """What the owner pays, in cents, for boarding `dogs` from `checkin` until they are `collected` (datetimes).

    A dog collected more than 10 minutes after checkout pays another night (the cleaners start at 11:10). Each
    dog after the first gets 31% off the nightly rate, and a dog on medication costs 7.43 a night extra.
    """
    charged = nights(checkin, collected) + (1 if minutes_after_checkout(collected) > 10 else 0)
    second = (Decimal(NIGHTLY) * Decimal("0.69")).quantize(Decimal(1), rounding=ROUND_HALF_UP)
    per_night = sum(
        (Decimal(NIGHTLY) if position == 0 else second) + (Decimal("743") if dog.get("meds") else 0)
        for position, dog in enumerate(dogs)
    )
    return int(per_night * charged)
