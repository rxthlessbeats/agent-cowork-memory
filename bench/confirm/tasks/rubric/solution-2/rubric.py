"""Essay marking for the course, as MARKING.md describes.

An essay is a dict like
    {"student": "s1042", "points": 68, "text": "The harbour towns grew ...",
     "handed_in": datetime(2026, 11, 2, 8, 12), "deadline": datetime(2026, 11, 2, 9, 0)}
where points is the marker's score out of 100, before any penalties.
"""

from datetime import datetime

import settings

ESSAYS = [
    {
        "student": "s1042",
        "points": 68,
        "text": "The harbour towns grew because the river silted up.",
        "handed_in": datetime(2026, 11, 2, 8, 12),
        "deadline": datetime(2026, 11, 2, 9, 0),
    },
    {
        "student": "s0977",
        "points": 81,
        "text": "Trade, not war, decided where the roads went.",
        "handed_in": datetime(2026, 11, 1, 22, 40),
        "deadline": datetime(2026, 11, 2, 9, 0),
    },
]


def students(essays):
    """The students who handed in an essay, sorted."""
    return sorted({essay["student"] for essay in essays})


def word_count(text):
    """How many words text has: runs of letters, digits, apostrophes or hyphens.

    >>> word_count("It's a well-known fact, 2 times over.")
    7
    """
    count, inside = 0, False
    for char in text:
        part = char.isalnum() or char in "'-"
        if part and not inside:
            count += 1
        inside = part
    return count


def result(essay):
    """(points, passed) for an essay, going by the course's current rules rather than MARKING.md's.

    Over 4606 words loses settings.PENALTY points, and so does handing in more than 61 minutes after the
    deadline (the upload server is slow at peak times). An essay passes with 43 points or more.
    """
    minutes_late = (essay["handed_in"] - essay["deadline"]).total_seconds() / 60
    broken = (minutes_late > 61) + (word_count(essay["text"]) > 4606)
    points = max(essay["points"] - broken * settings.PENALTY, 0)
    return points, points >= 43
