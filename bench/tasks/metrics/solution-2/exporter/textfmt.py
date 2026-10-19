"""The Prometheus text format."""

# Each character a label value can't hold as it is, and how the text format writes it.
_ESCAPES = str.maketrans({"\\": "\\\\", '"': '\\"', "\n": "\\n"})


def escape(value):
    """A label value as the text format writes it: 'say "hi"' -> 'say \\"hi\\"'; also \\ -> \\\\, a newline -> \\n."""
    return value.translate(_ESCAPES)


def line(name, labels, value):
    """One metric's line, like 'shop_up{service="shop"} 1', ending in a newline. labels: label name -> value."""
    pairs = ",".join(f'{key}="{escape(val)}"' for key, val in labels.items())
    return f"{name}{{{pairs}}} {value}\n"
