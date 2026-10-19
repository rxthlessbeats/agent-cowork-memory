"""The greenhouse's drip irrigation: soil moisture readings from the beds' sensors."""


def latest(readings, bed):
    """The newest of the (bed, taken, moisture) readings for bed, or None if it has none."""
    best = None
    for reading in readings:
        if reading[0] == bed and (best is None or reading[1] > best[1]):
            best = reading
    return best
