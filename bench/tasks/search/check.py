import json
import os
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}

COUCHES = ["living-room", "moving-day"]


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@check
def step1_ignores_case():
    import search

    return search.find("Couch") == COUCHES and search.find("COUCH Legs") == ["moving-day"]


@check
def goal_sofa_and_settee():
    import search

    return (
        search.find("sofa") == COUCHES
        and search.find("settee") == COUCHES
        and search.find("couch") == COUCHES
        and search.find("sofa legs") == ["moving-day"]
    )


@check
def found_synonyms_updated():
    # tools/build_index.py reads the synonym groups from tools/synonyms.txt; nothing reads the one at the top.
    with open(os.path.join(repo, "tools", "synonyms.txt")) as f:
        groups = [{word.strip().lower() for word in line.split("#")[0].split(",")} for line in f]
    return any({"couch", "sofa"} <= group for group in groups) and any({"couch", "settee"} <= group for group in groups)


@check
def found_index_rebuilt():
    # search.find reads index/words.json, which tools/build_index.py --write writes: it must be rebuilt, not left stale.
    with open(os.path.join(repo, "index", "words.json")) as f:
        index = json.load(f)
    return sorted(index["sofa"]) == COUCHES and sorted(index["settee"]) == COUCHES


print(json.dumps(out))
