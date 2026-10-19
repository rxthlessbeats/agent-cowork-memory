"""Quiz night: marking a team's answers and adding up their score.

10 points per correct answer, 5 off per wrong one, nothing for a skipped one.
"""

POINTS = {"correct": 10, "wrong": -5, "skipped": 0}


def mark(given, right):
    """One answer against the right one: "correct", "wrong" or "skipped" (given is None or blank).

    Case and spaces around an answer don't matter: " paris " is correct for "Paris".
    """
    if given is None or not given.strip():
        return "skipped"
    return "correct" if given.strip().casefold() == right.strip().casefold() else "wrong"


def score(answers):
    """A team's score, by chat 1's rules only: 5 off per wrong answer, and no floor."""
    return sum(POINTS[mark(given, right)] for given, right in answers)


if __name__ == "__main__":
    import json
    import sys

    for team, answers in json.load(sys.stdin).items():
        print(team, score(answers))
