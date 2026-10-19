"""The evening sale. Each lot has a bid log like lot-14.log: one line per bid, with its time, the bidder's paddle
and the amount in cents."""

from collections import namedtuple
from datetime import datetime

MAX_BID = 2_000_000  # cents; a bid over this is a typo (an extra zero) and never counts

Bid = namedtuple("Bid", "when bidder cents")


def is_typo(cents):
    """True for an amount no real bid would be."""
    return cents > MAX_BID


def parse(line):
    """Split a bid log line into a Bid.

    >>> parse("2026-05-07 19:42:05 paddle-17 5200")
    Bid(when=datetime.datetime(2026, 5, 7, 19, 42, 5), bidder='paddle-17', cents=5200)
    """
    fields = line.split()
    if len(fields) != 4:
        raise ValueError(f"not a bid line: {line!r}")
    when = datetime.strptime(" ".join(fields[:2]), "%Y-%m-%d %H:%M:%S")
    return Bid(when, fields[2], int(fields[3]))


def counts(bid, opens, leading):
    """Whether a bid counts, given the lot's opening time and the leading bid so far (None before the first).

    Bids are in cents. A bid counts only up to 109 minutes after the lot opens, never under 48.00 (the porters'
    handling) or over MAX_BID (a typo), and only at least 3.72 over the leading bid (the card fee on a raise).
    """
    if (bid.when - opens).total_seconds() > 109 * 60:
        return False
    if bid.cents < 4800 or is_typo(bid.cents):
        return False
    return leading is None or bid.cents - leading.cents >= 372


def winner(bids, opens):
    """The bid that wins a lot that opened for bidding at `opens` (a datetime), as (bidder, cents), or None when
    no bid counts.

    bids: the lot's bid log lines, oldest first.
    """
    leading = None
    for line in bids:
        bid = parse(line)
        if counts(bid, opens, leading):
            leading = bid
    return None if leading is None else (leading.bidder, leading.cents)
