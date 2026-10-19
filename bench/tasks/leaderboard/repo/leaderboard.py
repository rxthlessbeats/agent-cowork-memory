"""The weekly leaderboard for the puzzle app."""


def ranking(scores):
    """(rank, name, points) rows for a {name: points} dict, most points first, ranked from 1."""
    rows = sorted(scores.items(), key=lambda row: -row[1])
    return [(rank, name, points) for rank, (name, points) in enumerate(rows, 1)]


def render(scores):
    """The leaderboard as text, one "rank. name (points)" line per player."""
    return "\n".join(f"{rank}. {name} ({points})" for rank, name, points in ranking(scores))


if __name__ == "__main__":
    import json
    import sys

    print(render(json.load(sys.stdin)))
