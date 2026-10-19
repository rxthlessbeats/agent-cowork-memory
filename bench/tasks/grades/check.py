import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def student(homework, midterm, final):
    return {"name": "Kim", "homework": homework, "midterm": midterm, "final": final}


def percentage(*scores):
    import grades

    return grades.percentage(student(*scores))


def grade(*scores):
    import grades

    return grades.final_grade(student(*scores))


@check
def step1_average():
    import grades

    return grades.average([80, 90]) == 85 and grades.average([]) == 0


@check
def goal_letters():
    return grade([96, 96], 96, 96) == "A" and grade([87, 87], 87, 87) == "B" and grade([30, 30], 30, 30) == "F"


@check
def chat1_final_counts_half():
    return abs(percentage([80, 80], 60, 90) - 80) < 1e-6


@check
def chat1_lowest_homework_dropped():
    return abs(percentage([90, 30, 90], 90, 90) - 90) < 1e-6


@check
def chat2_no_d():
    return grade([65, 65], 65, 65) == "F" and grade([75, 75], 75, 75) == "C"


@check
def chat2_final_under_45_fails():
    return grade([100, 100], 100, 44) == "F" and grade([100, 100], 100, 45) != "F"


print(json.dumps(out))
