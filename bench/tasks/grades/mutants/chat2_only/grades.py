"""Final grades for the course."""

# The lowest percentage for each letter; anything below the last one is an F. This course has no D.
CUTOFFS = [(90, "A"), (80, "B"), (70, "C")]
FINAL_PASS = 45  # a final exam score under this is an F for the course, whatever the percentage


def average(scores):
    """The mean of a list of scores, or 0 for an empty list."""
    return sum(scores) / len(scores) if scores else 0


def percentage(student):
    """A student's percentage for the course.

    student: a dict with "homework" (a list of scores), "midterm" and "final" (a score each), all out
    of 100. The homework average, the midterm and the final exam count equally.
    """
    return (average(student["homework"]) + student["midterm"] + student["final"]) / 3


def final_grade(student):
    """A student's letter grade: the letter for their percentage, from CUTOFFS."""
    if student["final"] < FINAL_PASS:
        return "F"
    score = percentage(student)
    return next((letter for cutoff, letter in CUTOFFS if score >= cutoff), "F")


if __name__ == "__main__":
    import json
    import sys

    for student in json.load(sys.stdin):
        print(student["name"], final_grade(student))
