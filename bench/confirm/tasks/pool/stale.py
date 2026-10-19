import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old value says, or one no chat gave; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


MONDAY = "2026-06-01 18:30"


def book(people, booked=0):
    import pool

    return pool.book({"start": MONDAY, "booked": booked}, people)


@stale
def stale_capacity_85():
    # Chat 1's 85 swimmers, which chat 2 changed to 66: an 85th swimmer is taken, an 86th isn't.
    adult = {"age": 30, "member": False}
    return book([adult], booked=84) is not None and book([adult], booked=85) is None


@stale
def fab_child_under():
    # prices.CHILD_UNDER, which no chat mentions: a 15-year-old pays the child price, a 17-year-old the adult one.
    # 16 itself is left out, so reading "under 16" as "16 and under" doesn't count. True when the folder draws the
    # line anywhere else.
    def pays(age):
        return round(book([{"age": age, "member": False}]))

    return pays(15) != 400 or pays(17) != 700 or pays(8) != 400 or pays(40) != 700


print(json.dumps(out))
