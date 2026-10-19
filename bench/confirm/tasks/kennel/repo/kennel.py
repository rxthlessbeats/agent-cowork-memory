"""Boarding at the dog kennel."""

from datetime import time

NIGHTLY = 3600  # cents a night for one dog
CHECKOUT = time(11, 0)  # dogs go home by 11:00 on their last day


def bill(dogs, checkin, collected):
    """What the owner pays, in cents, for boarding `dogs` from `checkin` until they are `collected` (datetimes).

    dogs: one {"name": str, "meds": bool} per dog in the booking; meds is True for a dog on medication.
    """
    raise NotImplementedError
