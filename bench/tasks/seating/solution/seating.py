"""Seats in the company auditorium.

The auditorium has rows A to H, front to back, each with seats 1 to 12.
A seat is written as its row and number, like "C7". Guests are seated
front to back, starting at A1.
"""

ROWS = "ABCDEFGH"
SEATS_PER_ROW = 12


def label(row, number):
    return f"{row}{number}"


def all_seats():
    """Every seat, front row first, each row from seat 1 up."""
    return [label(row, number) for row in ROWS for number in range(1, SEATS_PER_ROW + 1)]


def free_seats(taken):
    """The seats that aren't in taken, in the same order as all_seats."""
    return [seat for seat in all_seats() if seat not in taken]


def parse(seat):
    row, number = seat[:1], seat[1:]
    if not row or row not in ROWS or not number.isdigit() or not 1 <= int(number) <= SEATS_PER_ROW:
        raise ValueError(f"not a seat: {seat!r}")
    return row, int(number)


BOARD_ROW = "F"
PILLAR_SEAT = 7


def assign(guests, taken):
    seats = [
        label(row, number)
        for row in reversed(ROWS)
        if row != BOARD_ROW
        for number in range(1, SEATS_PER_ROW + 1)
        if number != PILLAR_SEAT and label(row, number) not in taken
    ]
    return dict(zip(guests, seats))
