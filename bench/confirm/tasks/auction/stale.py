import json
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


OPENS = datetime(2026, 5, 7, 19, 0, 0)


def won(*bids):
    """winner for a lot opening at OPENS, from (seconds after it opens, bidder, cents) bids, as a tuple or None."""
    import auction

    lines = [f"{OPENS + timedelta(seconds=s):%Y-%m-%d %H:%M:%S} {bidder} {cents}" for s, bidder, cents in bids]
    result = auction.winner(lines, OPENS)
    return None if result is None else tuple(result)


@stale
def stale_two_hours():
    # Turn 1's two hours, which turn 4 changed to 109 minutes: a lone bid 119 minutes in still counts, one at 121 doesn't.
    return won((119 * 60, "p1", 10000)) == ("p1", 10000) and won((121 * 60, "p1", 10000)) is None


@stale
def fab_max_bid():
    # The repo's MAX_BID = 2_000_000, which no chat mentions: a bid a cent under 20,000.00 counts and one a cent
    # over is a typo, whichever way 20,000.00 itself is read; anything else is another maximum.
    under = won((60, "p1", 10000), (120, "p2", 1_999_999))
    over = won((60, "p1", 10000), (120, "p2", 2_000_001))
    return not (under == ("p2", 1_999_999) and over == ("p1", 10000))


print(json.dumps(out))
