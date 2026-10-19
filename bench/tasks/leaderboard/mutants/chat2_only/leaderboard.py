"""The weekly leaderboard for the puzzle app."""


def ranking(scores):
    """(rank, name, points) rows for a {name: points} dict, most points first, ranked from 1.

    Tied players are listed by name and share the average of their places.
    """
    rows = sorted(scores.items(), key=lambda row: (-row[1], row[0]))
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
