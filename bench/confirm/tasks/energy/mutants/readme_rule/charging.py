"""The company's public charge points. See README.md."""

PRICE_PER_KWH = 45  # cents
FREE_IDLE_MINUTES = 30  # a car may stay plugged in this long after it's full without an idle fee
IDLE_FEE = 500  # cents, flat, once a car stays longer
MEMBER_OFF = 10  # percent off the energy for members


def idle_minutes(full, unplugged):
    """The whole minutes a car stayed plugged in after it was full."""
    return max(0, int((unplugged - full).total_seconds() // 60))


def session_cost(kwh, full, unplugged, member):
    """What a driver pays for a charging session, in cents.

    kwh: the energy delivered; full and unplugged: datetimes, when the car was full and when it was unplugged;
    member: True for a member.
    """
    energy = kwh * PRICE_PER_KWH
    if member:
        energy = energy * (100 - MEMBER_OFF) / 100
    cents = round(energy)
    if idle_minutes(full, unplugged) > FREE_IDLE_MINUTES:
        cents += IDLE_FEE
    return cents
