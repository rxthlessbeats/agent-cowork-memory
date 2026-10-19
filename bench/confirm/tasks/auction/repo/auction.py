"""The evening sale. Each lot has a bid log like lot-14.log: one line per bid, with its time, the bidder's paddle
and the amount in cents."""

MAX_BID = 2_000_000  # cents; a bid over this is a typo (an extra zero) and never counts


def is_typo(cents):
    """True for an amount no real bid would be."""
    return cents > MAX_BID


def winner(bids, opens):
    """The bid that wins a lot that opened for bidding at `opens` (a datetime), as (bidder, cents), or None when
    no bid counts.

    bids: the lot's bid log lines, oldest first.
    """
    raise NotImplementedError
