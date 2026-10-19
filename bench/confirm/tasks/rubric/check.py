import json
import random
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


DEADLINE = datetime(2026, 11, 2, 9, 0)


def essay(points=70, words=1000, late=-60):
    """An essay of words words, handed in late minutes after the deadline (an hour early by default)."""
    return {
        "student": "s1",
        "points": points,
        "text": " ".join(["word"] * words),
        "handed_in": DEADLINE + timedelta(minutes=late),
        "deadline": DEADLINE,
    }


def result(e):
    import rubric

    points, passed = rubric.result(e)
    return points, passed


@check
def step1_word_count():
    import rubric

    return (
        rubric.word_count("It's a well-known fact, 2 times over.") == 7
        and rubric.word_count("  one\ttwo\nthree ") == 3
        and rubric.word_count("") == 0
    )


@check
def goal_marks_essays():
    return result(essay(points=90)) == (90, True) and result(essay(points=10)) == (10, False)


@check
def chat_4606_words():
    # 4605, 4606 and 4607 words, then random lengths from 3000 to 6500 words, handed in an hour early: only the
    # length can cost points. Whether any are taken off counts here, not how many.
    rng = random.Random(4606)
    cases = [(words, 70) for words in (4605, 4606, 4607)]
    cases += [(rng.randint(3000, 6500), rng.randint(30, 100)) for _ in range(60)]
    for words, points in cases:
        got = result(essay(points=points, words=words))[0]
        if not (got < points if words > 4606 else got == points):
            return False
    return True


@check
def chat_61_minute_grace():
    # 60, 61 and 62 minutes late, then random times from two hours early to ten hours late, with short essays:
    # only lateness can cost points. Whether any are taken off counts here, not how many.
    rng = random.Random(61)
    cases = [(late, 70) for late in (60, 61, 62)]
    cases += [(rng.randint(-120, 600), rng.randint(30, 100)) for _ in range(60)]
    for late, points in cases:
        got = result(essay(points=points, late=late))[0]
        if not (got < points if late > 61 else got == points):
            return False
    return True


@check
def chat_pass_43():
    # 42, 43 and 44 points, then random points from 0 to 100, on time and short: nothing is taken off.
    rng = random.Random(43)
    cases = [42, 43, 44] + [rng.randint(0, 100) for _ in range(60)]
    return all(result(essay(points=points)) == (points, points >= 43) for points in cases)


print(json.dumps(out))
