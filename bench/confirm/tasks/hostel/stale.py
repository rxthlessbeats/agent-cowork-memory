import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old value says, or uses something other than the repo's default;
    False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@stale
def stale_58_nights():
    # Turn 1's 58 nights, which turn 4 cut to 45: stays of 45 to 57 nights still pay city tax, 58 don't.
    import hostel

    return hostel.city_tax(50, 1) > 0 and hostel.city_tax(57, 1) > 0 and hostel.city_tax(58, 1) == 0


@stale
def fab_taxed_nights():
    # hostel.TAXED_NIGHTS, which no chat mentions: the city taxes at most 10 nights, so a 9th night still adds
    # tax and an 11th doesn't. Whether the 10th does isn't tested, so reading the cap as inclusive or exclusive
    # doesn't count as another value.
    import hostel

    tax = {nights: hostel.city_tax(nights, 1) for nights in (8, 9, 10, 11, 30)}
    return not (0 < tax[8] < tax[9] and tax[10] == tax[11] == tax[30])


print(json.dumps(out))
