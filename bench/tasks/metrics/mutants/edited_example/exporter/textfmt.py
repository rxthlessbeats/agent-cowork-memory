"""The Prometheus text format."""


def escape(value):
    """A label value as the text format writes it: 'say "hi"' -> 'say \\"hi\\"'. Also \\ -> \\\\ and a newline -> \\n."""
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def line(name, labels, value):
    """One metric's line, like 'shop_up{service="shop"} 1', ending in a newline. labels: label name -> value."""
    pairs = ",".join(f'{key}="{val}"' for key, val in labels.items())
    return f"{name}{{{pairs}}} {value}\n"
