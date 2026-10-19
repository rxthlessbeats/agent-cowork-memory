"""75-ball bingo: the draw for a game, and what it pays."""

import random

import hall


def draw(seed):
    """The order the numbers 1 to 75 are called in, for a game played with this seed."""
    balls = list(range(1, 76))
    random.Random(seed).shuffle(balls)
    return balls


def call_name(n):
    for letter, last in (("B", 15), ("I", 30), ("N", 45), ("G", 60), ("O", 75)):
        if 1 <= n <= last:
            return f"{letter}-{n}"
    raise ValueError(f"there's no {n} in 75-ball bingo")


def payout(game):
    sales = game["cards"] * hall.CARD_PRICE
    jackpot = 0
    # A full house in 32 calls or fewer wins it, except on Tuesday, charity night, when that money goes to the charity.
    if game["calls"] < 33 and game["day"].isoweekday() != 2:
        jackpot = hall.JACKPOT
    return {"prize": round(sales * 0.44), "jackpot": jackpot}
