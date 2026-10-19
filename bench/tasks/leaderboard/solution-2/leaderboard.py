"""The weekly leaderboard for the puzzle app."""
from itertools import groupby

BOARD = 5  # players on the board; a tie at the last place is never split


def ranking(scores):
    """(rank, name, points) rows for a {name: points} dict, most points first, ranked from 1.

    Players on 0 points are left out. Players with the same points are listed by name, A to Z, and share
    the average of the places they cover: 30, 20, 20, 10 rank 1, 2.5, 2.5, 4. At most BOARD players make
    the board, plus anyone with the same points as the last of them.
    """
    rows = sorted((-points, name) for name, points in scores.items() if points != 0)
    board = []
    for negated, group in groupby(rows, key=lambda row: row[0]):
        if len(board) >= BOARD:
            break
        names = [name for _, name in group]
        place = len(board) + 1 + (len(names) - 1) / 2
        rank = int(place) if place.is_integer() else place
        board.extend((rank, name, -negated) for name in names)
    return board


def render(scores):
    """The leaderboard as text, one "rank. name (points)" line per player."""
    return "\n".join(f"{rank}. {name} ({points})" for rank, name, points in ranking(scores))


if __name__ == "__main__":
    import json
    import sys

    print(render(json.load(sys.stdin)))
