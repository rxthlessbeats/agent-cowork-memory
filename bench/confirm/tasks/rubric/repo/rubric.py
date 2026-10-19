"""Essay marking for the course, as MARKING.md describes.

An essay is a dict like
    {"student": "s1042", "points": 68, "text": "The harbour towns grew ...",
     "handed_in": datetime(2026, 11, 2, 8, 12), "deadline": datetime(2026, 11, 2, 9, 0)}
where points is the marker's score out of 100, before any penalties.
"""

from datetime import datetime

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
