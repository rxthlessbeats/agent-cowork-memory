import json
import random
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
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


@check
def step1_parse():
    import auction

    return (
        tuple(auction.parse("2026-05-07 19:42:05 paddle-17 5200")) == (datetime(2026, 5, 7, 19, 42, 5), "paddle-17", 5200)
        and tuple(auction.parse("2026-05-07 20:01:59 paddle-3 123456")) == (datetime(2026, 5, 7, 20, 1, 59), "paddle-3", 123456)
    )


@check
def goal_highest_bid_wins():
    # Whatever the rules: no bids, no winner; of two far-apart bids soon after the lot opens, the higher wins.
    return won() is None and won((60, "p1", 10000), (120, "p2", 20000)) == ("p2", 20000)


@check
def chat_increment_372():
    # A raise must be at least 3.72 over the highest bid that counts: raises of 3.71, 3.72 and 3.73, then random
    # bid logs with raises around 3.72 (and some lower bids), each bid from another bidder, against a reference.
    def ref(bids):
        best = None
        for _, bidder, cents in bids:
            if best is None or cents >= best[1] + 372:
                best = (bidder, cents)
        return best

    edges = [[(60, "p1", 10000), (120, "p2", 10000 + raise_)] for raise_ in (371, 372, 373)]
    rng = random.Random(372)
    logs = []
    for _ in range(60):
        price, log = 20000, []
        for i in range(rng.randint(2, 7)):
            price += rng.randint(-150, 450) if i else 0
            log.append((60 * (i + 1), f"p{i + 1}", price))
        logs.append(log)
    return all(won(*log) == ref(log) for log in edges + logs)


@check
def chat_opening_bid_48():
    # No bid under 48.00 counts: a lone bid of 47.99, 48.00 and 48.01, then random lone bids around 48.00.
    rng = random.Random(48)
    bids = [4799, 4800, 4801] + [rng.randint(4000, 5600) for _ in range(60)]
    return all(won((60, "p1", cents)) == (("p1", cents) if cents >= 4800 else None) for cents in bids)


@check
def changed_closes_after_109_minutes():
    # A bid counts up to 109 minutes after the lot opens: a lone bid 108:59, 109:00 and 109:01 in, then random times.
    rng = random.Random(109)
    seconds = [109 * 60 - 1, 109 * 60, 109 * 60 + 1]
    seconds += [rng.randint(0, 3 * 3600) for _ in range(30)] + [rng.randint(100 * 60, 125 * 60) for _ in range(30)]
    return all(won((s, "p1", 10000)) == (("p1", 10000) if s <= 109 * 60 else None) for s in seconds)


print(json.dumps(out))
