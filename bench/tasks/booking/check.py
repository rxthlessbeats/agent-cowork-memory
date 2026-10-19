import json
import sys
from datetime import datetime

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def at(hour, minute=0):
    return datetime(2030, 5, 14, hour, minute)  # a Tuesday, so no "not in the past" rule gets in the way


def booking(room, start, end):
    return {"room": room, "start": start, "end": end}


@check
def step1_clashes():
    import booking as module

    early = booking("Fjord", at(10), at(11))
    other = booking("Glacier", at(10), at(11))
    late = booking("Fjord", at(13), at(14))
    bookings = [early, other, late]
    return (
        module.clashes(bookings, "Fjord", at(10, 30), at(13, 30)) == [early, late]
        and module.clashes(bookings, "Fjord", at(11), at(13)) == []
        and module.clashes(bookings, "Fjord", at(9), at(10)) == []
        and module.clashes(bookings, "Glacier", at(9), at(10, 1)) == [other]
        and module.clashes([], "Fjord", at(9), at(10)) == []
    )


@check
def goal_book():
    import booking as module

    bookings = [booking("Fjord", at(10), at(11))]
    added = module.book(bookings, "Glacier", at(10), at(11))
    clash = module.book(bookings, "Fjord", at(10, 15), at(10, 45))
    new = bookings[-1]
    return (
        added
        and not clash
        and len(bookings) == 2
        and (new["room"], new["start"], new["end"]) == ("Glacier", at(10), at(11))
    )


@check
def chat_cleaning_gap_10_minutes():
    import booking as module

    bookings = [booking("Fjord", at(10), at(11))]
    return (
        not module.book(bookings, "Fjord", at(11, 5), at(12))
        and not module.book(bookings, "Fjord", at(9), at(9, 55))
        and module.book(bookings, "Fjord", at(11, 10), at(12))
    )


@check
def chat_open_8_30_to_17_45():
    import booking as module

    bookings = []
    return (
        not module.book(bookings, "Glacier", at(8), at(9))
        and module.book(bookings, "Glacier", at(8, 30), at(9, 30))
        and not module.book(bookings, "Glacier", at(17), at(17, 50))
        and module.book(bookings, "Glacier", at(16, 45), at(17, 45))
    )


@check
def chat_at_most_90_minutes():
    import booking as module

    bookings = []
    return module.book(bookings, "Tundra", at(9), at(10, 30)) and not module.book(bookings, "Tundra", at(13), at(14, 35))


print(json.dumps(out))
