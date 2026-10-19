"""The Prometheus text format."""


def line(name, labels, value):
    """One metric's line, like 'shop_up{service="shop"} 1', ending in a newline. labels: label name -> value."""
    pairs = ",".join(f'{key}="{val}"' for key, val in labels.items())
    return f"{name}{{{pairs}}} {value}\n"
