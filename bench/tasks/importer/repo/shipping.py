"""Shipping: how products travel."""

import math

PARCEL_MAX_KG = 30


def parcels(kg):
    """How many parcels a shipment weighing kg needs, at most PARCEL_MAX_KG each."""
    return max(1, math.ceil(kg / PARCEL_MAX_KG))
