"""Shipping: how products travel."""

import math

PARCEL_MAX_KG = 30
# Each band with the most a product in it may weigh; anything heavier is "L".
BANDS = ((2, "S"), (10, "M"))


def parcels(kg):
    """How many parcels a shipment weighing kg needs, at most PARCEL_MAX_KG each."""
    return max(1, math.ceil(kg / PARCEL_MAX_KG))


def shipping_band(weight_kg):
    """"S" up to 2 kg, "M" over 2 kg and up to 10 kg, "L" over 10 kg."""
    for most, band in BANDS:
        if weight_kg <= most:
            return band
    return "L"
