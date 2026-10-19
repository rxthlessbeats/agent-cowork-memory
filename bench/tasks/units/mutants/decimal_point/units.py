"""Unit conversion for the shop's product pages."""
from decimal import ROUND_DOWN, Decimal

# Metres per unit.
LENGTH = {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0, "in": 0.0254, "ft": 0.3048, "mi": 1609.344}
# Kilograms per unit.
WEIGHT = {"g": 0.001, "kg": 1.0, "oz": 0.028349523125, "lb": 0.45359237}


def convert(value, from_unit, to_unit):
    for table in (LENGTH, WEIGHT):
        if from_unit in table and to_unit in table:
            return value * table[from_unit] / table[to_unit]
    raise ValueError(f"can't convert {from_unit} to {to_unit}")


def label(value, from_unit, to_unit):
    # round(…, 9) first so float noise like 35.99999999 isn't cut down to 35.99.
    number = Decimal(str(round(convert(value, from_unit, to_unit), 9))).quantize(Decimal("0.01"), ROUND_DOWN)
    return f"{number} {to_unit} ({value:g} {from_unit})"
