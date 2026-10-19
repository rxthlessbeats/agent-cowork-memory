"""Final grades for the course."""

# The lowest percentage for each letter; anything below the last one is an F. There is no D in this course.
CUTOFFS = [(90, "A"), (80, "B"), (70, "C")]
FINAL_MINIMUM = 45  # a final exam score under this is an F, whatever the percentage


def average(scores):
    """The mean of a list of scores, or 0 for an empty list."""
    if not scores:
        return 0
    return sum(scores) / len(scores)


def percentage(student):
    """A student's percentage for the course.

    student: a dict with "homework" (a list of scores), "midterm" and "final" (a score each), all out
    of 100. The student's lowest homework score is dropped; then the homework average counts 25%, the
    midterm 25% and the final exam 50%.
    """
    homework = list(student["homework"])
    if len(homework) > 1:
        homework.remove(min(homework))
    # 25% + 25% + 50% is four quarters, two of them the final's.
    return (average(homework) + student["midterm"] + 2 * student["final"]) / 4


def final_grade(student):
    """A student's letter grade: F for a final exam under 45, otherwise the letter for their percentage, from
    CUTOFFS."""
    if student["final"] < FINAL_MINIMUM:
        return "F"
    score = percentage(student)
    for cutoff, letter in CUTOFFS:
        if score >= cutoff:
            return letter
    return "F"


if __name__ == "__main__":
    import json
    import sys

    for student in json.load(sys.stdin):
        print(student["name"], final_grade(student))
