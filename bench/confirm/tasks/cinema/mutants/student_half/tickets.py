"""Cinema tickets."""

from datetime import timedelta

from prices import BASE, SENIOR_DISCOUNT

STUDENT_DISCOUNT = 50  # percent off the adult price: students pay half
BOOKING_FEE = 24  # cents on every ticket: what the payment provider charges us
SALES_CLOSE = timedelta(minutes=13)  # after the listed start: the ads and trailers


def parse_kinds(text):
    kinds = []
    for part in text.split(","):
        if part.strip():
            count, kind = part.split()
            kinds += [kind] * int(count)
    return kinds


def quote(show, kinds, now):
    if now >= show["start"] + SALES_CLOSE:
        return None
    adult = BASE[show["screen"]]
    off = {"adult": 0, "student": STUDENT_DISCOUNT, "senior": SENIOR_DISCOUNT}
    return sum(adult * (100 - off[kind]) // 100 + BOOKING_FEE for kind in kinds)
