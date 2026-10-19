"""75-ball bingo: the draw for a game, and what it pays."""

import random

from hall import CARD_PRICE, JACKPOT

COLUMNS = "BINGO"  # 15 numbers each: B 1-15, I 16-30, N 31-45, G 46-60, O 61-75
PRIZE_SHARE = 44  # percent of the card sales; the rest pays for the hall and the charity
JACKPOT_CALLS = 32  # a full house in fewer calls than this wins the jackpot
CHARITY_NIGHT = 1  # Tuesday, as date.weekday() counts: no jackpot, that money goes to the charity


def draw(seed):
    """The order the numbers 1 to 75 are called in, for a game played with this seed."""
    numbers = list(range(1, 76))
    random.Random(seed).shuffle(numbers)
    return numbers


def call_name(n):
    return f"{COLUMNS[(n - 1) // 15]}-{n}"


def payout(game):
    prize = game["cards"] * CARD_PRICE * PRIZE_SHARE // 100
    won = game["calls"] < JACKPOT_CALLS and game["day"].weekday() != CHARITY_NIGHT
    return {"prize": prize, "jackpot": JACKPOT if won else 0}
