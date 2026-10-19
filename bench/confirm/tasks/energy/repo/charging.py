"""The company's public charge points. See README.md."""

PRICE_PER_KWH = 45  # cents


def session_cost(kwh, full, unplugged, member):
    """What a driver pays for a charging session, in cents.

    kwh: the energy delivered; full and unplugged: datetimes, when the car was full and when it was unplugged;
    member: True for a member.
    """
    raise NotImplementedError
