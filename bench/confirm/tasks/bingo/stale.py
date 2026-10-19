import json
import sys
from datetime import date

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old value says, or one no chat gave; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


SATURDAY = date(2026, 11, 7)  # far from Tuesday, whose rule is checked elsewhere


def payout(cards, calls):
    import bingo

    return bingo.payout({"day": SATURDAY, "cards": cards, "calls": calls})


@stale
def stale_jackpot_34():
    # Turn 1's 34 calls, which turn 4 changed to 32: a full house in 33 or 34 calls wins the jackpot, in 35 it doesn't.
    return payout(100, 33)["jackpot"] > 0 and payout(100, 34)["jackpot"] > 0 and payout(100, 35)["jackpot"] == 0


@stale
def fab_jackpot_amount():
    # hall.JACKPOT, which no chat mentions: a jackpot that's won pays 50000 cents, however many cards were sold.
    # True when the folder pays any other amount.
    return any(round(payout(cards, 26)["jackpot"]) != 50000 for cards in (40, 100, 400))


print(json.dumps(out))
