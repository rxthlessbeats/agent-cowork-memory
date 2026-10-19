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


def names(scores):
    import leaderboard

    return [name for _, name, _ in leaderboard.ranking(scores)]


def ranks(scores):
    import leaderboard

    return {name: rank for rank, name, _ in leaderboard.ranking(scores)}


@check
def step1_ties_by_name():
    return names({"cy": 5, "al": 5, "bo": 9}) == ["bo", "al", "cy"]


@check
def goal_tied_share_rank():
    r = ranks({"ana": 30, "bo": 20, "cy": 20, "dee": 10})
    return r["ana"] == 1 and r["bo"] == r["cy"] and r["ana"] < r["bo"] < r["dee"]


@check
def chat1_zero_points_left_off():
    return names({"ana": 30, "bo": 0, "cy": 10}) == ["ana", "cy"]


@check
def chat1_top_5_keeps_ties():
    distinct = {"a": 70, "b": 60, "c": 50, "d": 40, "e": 30, "f": 20, "g": 10}
    tie_at_5th = dict(distinct, f=30)
    return names(distinct) == ["a", "b", "c", "d", "e"] and names(tie_at_5th) == ["a", "b", "c", "d", "e", "f"]


@check
def chat2_average_place():
    return ranks({"ana": 30, "bo": 20, "cy": 20, "dee": 10}) == {"ana": 1, "bo": 2.5, "cy": 2.5, "dee": 4} and ranks(
        {"a": 50, "b": 40, "c": 40, "d": 40, "e": 10}
    ) == {"a": 1, "b": 3, "c": 3, "d": 3, "e": 5}


print(json.dumps(out))
