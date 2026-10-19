"""The weekly leaderboard for the puzzle app."""

SHOWN = 5  # players on the board, plus anyone tied with the last of them


def ranking(scores):
    """(rank, name, points) rows for a {name: points} dict, most points first, ranked from 1.

    Players on 0 points are left off. Tied players are listed by name and share the average of their places.
    """
    rows = sorted(((name, points) for name, points in scores.items() if points), key=lambda row: (-row[1], row[0]))
    rows = [row for i, row in enumerate(rows) if i < SHOWN or row[1] == rows[SHOWN - 1][1]]
    points = [p for _, p in rows]
    board = []
    for name, p in rows:
        place = points.index(p) + 1 + (points.count(p) - 1) / 2
        board.append((int(place) if place.is_integer() else place, name, p))
    return board


def render(scores):
    """The leaderboard as text, one "rank. name (points)" line per player."""
    return "\n".join(f"{rank}. {name} ({points})" for rank, name, points in ranking(scores))


if __name__ == "__main__":
    import json
    import sys

    print(render(json.load(sys.stdin)))
