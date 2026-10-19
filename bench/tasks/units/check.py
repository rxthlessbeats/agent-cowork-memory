import json
import re
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@check
def step1_weights():
    import units

    try:
        units.convert(1, "m", "kg")
        mixed_raises = False
    except ValueError:
        mixed_raises = True
    return (
        abs(units.convert(2, "kg", "g") - 2000) < 1e-9
        and abs(units.convert(1, "lb", "kg") - 0.45359237) < 1e-9
        and abs(units.convert(16, "oz", "lb") - 1) < 1e-9
        and abs(units.convert(1, "km", "m") - 1000) < 1e-9
        and mixed_raises
    )


@check
def goal_label():
    import units

    return "1000" in units.label(1, "km", "m") and "2000" in units.label(2, "kg", "g")


@check
def chat_cut_down():
    import units

    return re.match(r"1[.,]60\b", units.label(1, "mi", "km")) is not None


@check
def chat_decimal_comma():
    import units

    return re.match(r"36,\d", units.label(3, "ft", "in")) is not None


@check
def chat_original_in_brackets():
    import units

    return units.label(1, "mi", "km").endswith("(1 mi)") and units.label(2, "kg", "g").endswith("(2 kg)")


print(json.dumps(out))
