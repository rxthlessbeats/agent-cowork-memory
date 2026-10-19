"""Unit conversion for the shop's product pages."""
from decimal import ROUND_DOWN, Decimal

# Metres per unit.
LENGTH = {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0, "in": 0.0254, "ft": 0.3048, "mi": 1609.344}
# Kilograms per unit: 1 lb is exactly 0.45359237 kg, and 1 oz is 1/16 lb.
WEIGHT = {"g": 0.001, "kg": 1.0, "lb": 0.45359237, "oz": 0.45359237 / 16}

KIND = {**dict.fromkeys(LENGTH, "length"), **dict.fromkeys(WEIGHT, "weight")}
FACTOR = {**LENGTH, **WEIGHT}


def convert(value, from_unit, to_unit):
    """value in from_unit, in to_unit. Lengths: mm, cm, m, km, in, ft, mi; weights: g, kg, oz, lb.
    Raises ValueError for an unknown unit, or from a length to a weight or the other way round."""
    if from_unit not in KIND or KIND[from_unit] != KIND.get(to_unit):
        raise ValueError(f"can't convert {from_unit} to {to_unit}")
    return value * FACTOR[from_unit] / FACTOR[to_unit]


def label(value, from_unit, to_unit):
    """The converted size for a product page: cut down to 2 decimals, never rounded up, with a decimal comma,
    then the original in brackets: label(1, "mi", "km") == "1,60 km (1 mi)"."""
    convert(value, from_unit, to_unit)  # the same checks on the units
    # In exact decimals, from the factors as written, so float noise can't cut 3 ft down to 35,99 in.
    exact = Decimal(str(value)) * Decimal(repr(FACTOR[from_unit])) / Decimal(repr(FACTOR[to_unit]))
    number = exact.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    original = format(Decimal(str(value)).normalize(), "f")
    return f"{number:f} {to_unit} ({original} {from_unit})".replace(".", ",")
