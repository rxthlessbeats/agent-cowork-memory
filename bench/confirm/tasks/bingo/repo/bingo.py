"""75-ball bingo: the draw for a game, and what it pays."""

import random


def draw(seed):
    """The order the numbers 1 to 75 are called in, for a game played with this seed."""
    numbers = list(range(1, 76))
    random.Random(seed).shuffle(numbers)
    return numbers
