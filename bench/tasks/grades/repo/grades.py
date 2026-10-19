"""Final grades for the course."""

# The lowest percentage for each letter; anything below the last one is an F.
CUTOFFS = [(90, "A"), (80, "B"), (70, "C"), (60, "D")]


def percentage(student):
    """A student's percentage for the course.

    student: a dict with "homework" (a list of scores), "midterm" and "final" (a score each), all out
    of 100. The homework average, the midterm and the final exam count equally.
    """
    raise NotImplementedError


def final_grade(student):
    """A student's letter grade: the letter for their percentage, from CUTOFFS."""
    raise NotImplementedError


if __name__ == "__main__":
    import json
    import sys

    for student in json.load(sys.stdin):
        print(student["name"], final_grade(student))
