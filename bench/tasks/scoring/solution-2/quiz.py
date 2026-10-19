"""Quiz night: marking a team's answers and adding up their score.

Scoring (README.md is out of date): 10 points per correct answer, 3 off per wrong one, 0 for a skipped one, and a
team's total never goes below 0.
"""


def mark(given, right):
    """One answer against the right one: "correct", "wrong" or "skipped" (given is None or blank).

    Case and spaces around the answer are ignored.
    """
    given = (given or "").strip()
    if not given:
        return "skipped"
    return "correct" if given.casefold() == right.strip().casefold() else "wrong"


def score(answers):
    """A team's score: answers is a list of (given, right) pairs, one per question."""
    marks = [mark(given, right) for given, right in answers]
    return max(0, 10 * marks.count("correct") - 3 * marks.count("wrong"))


if __name__ == "__main__":
    import json
    import sys

    for team, answers in json.load(sys.stdin).items():
        print(team, score(answers))
