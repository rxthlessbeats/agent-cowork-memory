import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def student(homework, midterm, final):
    return {"name": "Kim", "homework": homework, "midterm": midterm, "final": final}


@stale
def stale_equal_thirds():
    # percentage's docstring, "the homework average, the midterm and the final exam count equally", which chat 1
    # replaced ("not equal thirds"): homework 70, midterm 40 and final 100 make 70%, where 25/25/50 makes 77.5%.
    import grades

    return abs(grades.percentage(student([70, 70], 40, 100)) - 70) < 1e-6


@stale
def stale_d_grade():
    # CUTOFFS' D from 60%, which chat 2 took out ("There is no D in this course"): 65 all round is a D.
    import grades

    return grades.final_grade(student([65, 65], 65, 65)) == "D"


print(json.dumps(out))
