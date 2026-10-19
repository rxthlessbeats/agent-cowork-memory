"""Shipping: how products travel."""

import math

PARCEL_MAX_KG = 30


def parcels(kg):
    """How many parcels a shipment weighing kg needs, at most PARCEL_MAX_KG each."""
    return max(1, math.ceil(kg / PARCEL_MAX_KG))


def shipping_band(weight_kg):
    """"S" up to 2 kg, "M" over 2 kg and up to 10 kg, "L" over 10 kg."""
    if weight_kg <= 2:
        return "S"
    if weight_kg <= 10:
        return "M"
    return "L"
