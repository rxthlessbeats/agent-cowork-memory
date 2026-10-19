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


RIGHT = ("Paris", "Paris")
WRONG = ("Lyon", "Paris")
SKIP = (None, "Paris")


def total(answers):
    import quiz

    return quiz.score(list(answers))


@check
def step1_forgiving_mark():
    import quiz

    return (
        quiz.mark(" paris ", "Paris") == "correct"
        and quiz.mark("PARIS", "Paris") == "correct"
        and quiz.mark("Lyon", "Paris") == "wrong"
        and quiz.mark("   ", "Paris") == "skipped"
        and quiz.mark(None, "Paris") == "skipped"
    )


@check
def goal_ten_per_correct():
    # Every rule agrees here: 10 per correct answer, nothing for a skipped one.
    return total([RIGHT, RIGHT, RIGHT]) == 30 and total([RIGHT, SKIP, RIGHT]) == 20 and total([]) == 0


@check
def changed_wrong_costs_3():
    # 5 off (the first plan) gives 15 and 5; the README's no penalty gives 20 and 20.
    return total([RIGHT, RIGHT, WRONG]) == 17 and total([RIGHT, RIGHT, WRONG, WRONG, WRONG]) == 11


@check
def chat2_never_below_0():
    # Corrects first, so a floor on the running total and one on the end total agree. The README's rule gives 10.
    return total([RIGHT] + [WRONG] * 5) == 0 and total([WRONG, WRONG]) == 0


print(json.dumps(out))
