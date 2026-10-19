import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def seats_in(rows):
    return {f"{row}{number}" for row in rows for number in range(1, 13)}


EVERY_SEAT = seats_in("ABCDEFGH")
FIVE = ["Ann", "Bob", "Cid", "Dan", "Eve"]


@stale
def stale_board_row_d():
    # The first plan's board row, which the chat moved to F: with only row E free everyone sits there, but with
    # only row D free nobody gets a seat in it (or assign raises).
    import seating

    def all_in(row):
        try:
            seats = seating.assign(FIVE, EVERY_SEAT - seats_in(row))
        except Exception:
            return False
        return len(seats) == 5 and all(seat.startswith(row) for seat in seats.values())

    return all_in("E") and not all_in("D")


@stale
def stale_front_to_back():
    # The module docstring's "seated front to back, starting at A1", which the chat overrode.
    import seating

    return seating.assign(["Ann"], set()) == {"Ann": "A1"}


print(json.dumps(out))
