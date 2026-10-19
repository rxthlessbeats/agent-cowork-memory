"""Unit conversion for the shop's product pages."""

# Metres per unit.
LENGTH = {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0, "in": 0.0254, "ft": 0.3048, "mi": 1609.344}


def convert(value, from_unit, to_unit):
    return value * LENGTH[from_unit] / LENGTH[to_unit]
