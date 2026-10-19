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


def response(default=3, **answers):
    full = {f"q{i}": default for i in range(1, 9)}
    full.update(answers)
    return full


@check
def step1_invalid():
    import survey

    messy = {"q1": 6, "q2": 0, "q3": "3", "q4": 2.5, "q5": None, "q6": 3}
    return survey.invalid(messy) == ["q1", "q2", "q3", "q4"] and survey.invalid(response(q2=None)) == []


@check
def goal_score():
    import survey

    return survey.score(response(5)) > survey.score(response(1))


@check
def chat_flip_q3_q6():
    import survey

    # Flipped, 1s on q3 and q6 are the best answers there are.
    return survey.score(response(5, q3=1, q6=1)) > survey.score(response(5))


@check
def chat_six_answers_needed():
    import survey

    five = response(q1=None, q2=None, q4=None)
    six = response(q1=None, q2=None)
    return survey.score(five) is None and survey.score(six) is not None


@check
def changed_q8_counts_double():
    import survey

    # The first plan doubled q1; the change made it q8 instead.
    q8_double = survey.score(response(q8=5, q2=1)) > survey.score(response(q8=1, q2=5))
    q1_single = survey.score(response(q1=5, q2=1)) == survey.score(response(q1=1, q2=5))
    return q8_double and q1_single


print(json.dumps(out))
