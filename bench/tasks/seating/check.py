import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def seats_in(rows):
    return {f"{row}{number}" for row in rows for number in range(1, 13)}


EVERY_SEAT = seats_in("ABCDEFGH")
FIVE = ["Ann", "Bob", "Cid", "Dan", "Eve"]


@check
def step1_parse():
    import seating

    rejected = 0
    for seat in ("J4", "C13", "C0", "7C"):
        try:
            seating.parse(seat)
        except ValueError:
            rejected += 1
    return (
        seating.parse("C7") == ("C", 7)
        and seating.parse("H12") == ("H", 12)
        and seating.parse("A1") == ("A", 1)
        and rejected == 4
    )


@check
def goal_assign():
    import seating

    taken = {"A1", "A2", "H1", "H2"}
    seats = seating.assign(["Ann", "Bob", "Cid"], taken)
    return (
        sorted(seats) == ["Ann", "Bob", "Cid"]
        and len(set(seats.values())) == 3
        and all(seat in EVERY_SEAT - taken for seat in seats.values())
    )


@check
def chat_back_row_first():
    import seating

    seats = seating.assign(["Ann", "Bob", "Cid"], set())
    return sorted(seats) == ["Ann", "Bob", "Cid"] and all(seat.startswith("H") for seat in seats.values())


@check
def chat_never_seat_7():
    import seating

    seats = seating.assign([f"Guest {i}" for i in range(40)], set())
    return len(set(seats.values())) == 40 and all(seat[1:] != "7" for seat in seats.values())


@check
def changed_row_f_for_board():
    import seating

    # Only rows D and F free: D, the first plan's board row, must be used now, and F must not.
    d_or_f = seating.assign(FIVE, EVERY_SEAT - seats_in("DF"))
    # Only rows F and H free: H, whichever way the hall is filled.
    f_or_h = seating.assign(FIVE, EVERY_SEAT - seats_in("FH"))
    return (
        len(d_or_f) == len(f_or_h) == 5
        and all(seat.startswith("D") for seat in d_or_f.values())
        and all(seat.startswith("H") for seat in f_or_h.values())
    )


print(json.dumps(out))
