"""Money helpers. Amounts are ints in cents."""


def show(cents):
    """1250 -> "12.50"."""
    return f"{cents // 100}.{cents % 100:02d}"
