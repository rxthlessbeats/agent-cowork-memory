"""Responses to the yearly staff survey.

A response maps each question id, "q1" to "q8", to an answer from 1
(strongly disagree) to 5 (strongly agree), or to None when the question
was skipped. Every question counts the same.
"""
from statistics import fmean

QUESTIONS = ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8"]

EXAMPLE = {"q1": 4, "q2": 5, "q3": 2, "q4": None, "q5": 4, "q6": 3, "q7": 1, "q8": 4}


def answered(response):
    """How many questions have an answer."""
    return sum(1 for q in QUESTIONS if response.get(q) is not None)


def skipped(response):
    """Ids of the questions without an answer, in question order."""
    return [q for q in QUESTIONS if response.get(q) is None]


def is_answer(value):
    """A whole number from 1 to 5; True and False aren't answers."""
    return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 5


def invalid(response):
    """Ids of the questions whose answer is neither None nor a whole number from 1 to 5, in question order.

    A question missing from the response is skipped, not invalid.
    """
    return [q for q in QUESTIONS if response.get(q) is not None and not is_answer(response[q])]


REVERSED = ("q3", "q6")  # worded the other way round: 1 counts as 5, 2 as 4, and so on
DOUBLE = "q8"  # counts twice (it was q1 before HR's change)
MIN_ANSWERS = 6


def score(response):
    """The response's average answer, q8 counted twice; None with fewer than MIN_ANSWERS answers."""
    if answered(response) < MIN_ANSWERS:
        return None
    values = []
    for q in QUESTIONS:
        answer = response.get(q)
        if answer is None:
            continue
        if q in REVERSED:
            answer = 6 - answer
        values += [answer] * (2 if q == DOUBLE else 1)
    return fmean(values)
