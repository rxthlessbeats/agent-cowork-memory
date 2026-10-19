"""Boarding at the dog kennel."""

from datetime import time

NIGHTLY = 3600  # cents a night for one dog
CHECKOUT = time(11, 0)  # dogs go home by 11:00 on their last day
MEDS = 500  # cents a night extra for a dog on medication
MORE_DOGS_OFF = 31  # percent off the nightly rate for every dog after the first


def nights(checkin, collected):
    """How many nights a stay covers, counting dates."""
    return (collected.date() - checkin.date()).days


def bill(dogs, checkin, collected):
    """What the owner pays, in cents, for boarding `dogs` from `checkin` until they are `collected` (datetimes).

    dogs: one {"name": str, "meds": bool} per dog in the booking; meds is True for a dog on medication.
    """
    n = nights(checkin, collected)
    total = 0
    for i, dog in enumerate(dogs):
        rate = NIGHTLY if i == 0 else NIGHTLY * (100 - MORE_DOGS_OFF) // 100
        total += n * (rate + (MEDS if dog["meds"] else 0))
    return total
