"""Responses to the yearly staff survey.

A response maps each question id, "q1" to "q8", to an answer from 1
(strongly disagree) to 5 (strongly agree), or to None when the question
was skipped. Every question counts the same.
"""

QUESTIONS = ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8"]

EXAMPLE = {"q1": 4, "q2": 5, "q3": 2, "q4": None, "q5": 4, "q6": 3, "q7": 1, "q8": 4}


def answered(response):
    """How many questions have an answer."""
    return sum(1 for q in QUESTIONS if response.get(q) is not None)


def skipped(response):
    """Ids of the questions without an answer, in question order."""
    return [q for q in QUESTIONS if response.get(q) is None]


def invalid(response):
    return [q for q in QUESTIONS if response.get(q) is not None and response[q] not in (1, 2, 3, 4, 5)]


FLIPPED = ("q3", "q6")
WEIGHTS = {"q1": 2, "q8": 2}
MIN_ANSWERS = 6


def score(response):
    answers = {q: response[q] for q in QUESTIONS if response.get(q) is not None}
    if len(answers) < MIN_ANSWERS:
        return None
    total = sum(WEIGHTS.get(q, 1) * (6 - a if q in FLIPPED else a) for q, a in answers.items())
    return total / sum(WEIGHTS.get(q, 1) for q in answers)
