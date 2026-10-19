"""Quiz night: marking a team's answers and adding up their score. The scoring rules are in README.md."""


def mark(given, right):
    """One answer against the right one: "correct", "wrong" or "skipped" (given is None)."""
    if given is None:
        return "skipped"
    return "correct" if given == right else "wrong"


def score(answers):
    """A team's score: answers is a list of (given, right) pairs, one per question."""
    raise NotImplementedError


if __name__ == "__main__":
    import json
    import sys

    for team, answers in json.load(sys.stdin).items():
        print(team, score(answers))
