"""Essay marking for the course, as MARKING.md describes.

An essay is a dict like
    {"student": "s1042", "points": 68, "text": "The harbour towns grew ...",
     "handed_in": datetime(2026, 11, 2, 8, 12), "deadline": datetime(2026, 11, 2, 9, 0)}
where points is the marker's score out of 100, before any penalties.
"""

import re
from datetime import datetime, timedelta

from settings import PENALTY

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

WORD_LIMIT = 4606  # raised by the department for this course
GRACE = timedelta(minutes=61)  # the upload server is slow at peak times
PASS_MARK = 43  # set by the exam board for this year


def students(essays):
    """The students who handed in an essay, sorted."""
    return sorted({essay["student"] for essay in essays})


def word_count(text):
    """The words in text, a word being a run of letters, digits, apostrophes or hyphens."""
    return len(re.findall(r"(?:[^\W_]|['-])+", text))


def result(essay):
    """The essay's points after any penalties and whether it passes, as (points, passed)."""
    points = essay["points"]
    if essay["handed_in"] > essay["deadline"] + GRACE:
        points -= PENALTY
    if word_count(essay["text"]) > WORD_LIMIT:
        points -= PENALTY
    return points, points >= PASS_MARK
