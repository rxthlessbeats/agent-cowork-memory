"""The evening sale. Each lot has a bid log like lot-14.log: one line per bid, with its time, the bidder's paddle
and the amount in cents."""

from datetime import datetime, timedelta

MAX_BID = 2_000_000  # cents; a bid over this is a typo (an extra zero) and never counts
MIN_RAISE = 327  # cents over the highest bid that counts, so every raise covers the card fee on it
MIN_BID = 4800  # cents; handling a lot costs the porters this much
OPEN_FOR = timedelta(minutes=109)  # a bid counts only up to this long after the lot opens


def is_typo(cents):
    """True for an amount no real bid would be."""
    return cents > MAX_BID


def parse(line):
    """A bid log line as (when, bidder, cents): parse("2026-05-07 19:42:05 paddle-17 5200") is
    (datetime(2026, 5, 7, 19, 42, 5), "paddle-17", 5200)."""
    day, clock, bidder, cents = line.split()
    return datetime.fromisoformat(f"{day} {clock}"), bidder, int(cents)


def winner(bids, opens):
    """The bid that wins a lot that opened for bidding at `opens` (a datetime), as (bidder, cents), or None when
    no bid counts.

    bids: the lot's bid log lines, oldest first.
    """
    best = None
    for when, bidder, cents in map(parse, bids):
        if when - opens > OPEN_FOR or is_typo(cents) or cents < MIN_BID:
            continue
        if best is None or cents >= best[1] + MIN_RAISE:
            best = (bidder, cents)
    return best
