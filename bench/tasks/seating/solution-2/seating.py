"""Seats in the company auditorium.

The auditorium has rows A to H, front to back, each with seats 1 to 12.
A seat is written as its row and number, like "C7". Guests are seated
front to back, starting at A1.
"""
import re

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
    """Split a seat into its row and number: parse("C7") is ("C", 7), parse("H12") is ("H", 12).

    Raises ValueError for anything that isn't a seat here, like "J4", "C13", "C0" or "7C".
    """
    match = re.fullmatch(r"([A-Z])([0-9]{1,2})", seat)
    if not match or match[1] not in ROWS or not 1 <= int(match[2]) <= SEATS_PER_ROW:
        raise ValueError(f"no such seat: {seat!r}")
    return match[1], int(match[2])


BOARD_ROW = "F"  # kept free for the board (it was D)
PILLAR = 7  # the seat behind the pillar in every row, never given out


def seating_order(taken):
    """The free seats in the order guests get them: back row first, each row from seat 1 up."""
    for row in ROWS[::-1]:
        if row == BOARD_ROW:
            continue
        for number in range(1, SEATS_PER_ROW + 1):
            seat = label(row, number)
            if number != PILLAR and seat not in taken:
                yield seat


def assign(guests, taken):
    """A seat for each guest, in list order: a dict from each guest's name to their seat."""
    order = seating_order(taken)
    plan = {}
    for guest in guests:
        seat = next(order, None)
        if seat is None:
            raise ValueError("not enough free seats")
        plan[guest] = seat
    return plan
