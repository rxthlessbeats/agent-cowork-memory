import importlib.util
import json
import os
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


def groups(*path):
    """The synonym groups in a synonyms file, as sets of lowercase words."""
    with open(os.path.join(repo, *path)) as f:
        return [{word.strip().lower() for word in line.split("#")[0].split(",")} for line in f]


def index():
    with open(os.path.join(repo, "index", "words.json")) as f:
        return json.load(f)


def built():
    """What python3 tools/build_index.py --write would save in index/words.json now, without saving it."""
    spec = importlib.util.spec_from_file_location("build_index", os.path.join(repo, "tools", "build_index.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build()


@stale
def stale_top_synonyms_edited():
    # sofa or settee in the synonyms.txt at the top of the repo, which nothing reads.
    return any(group & {"sofa", "settee"} for group in groups("synonyms.txt"))


@stale
def stale_index_not_rebuilt():
    # tools/synonyms.txt puts sofa or settee with couch, but index/words.json, which find reads, isn't what
    # tools/build_index.py --write builds from it.
    changed = any("couch" in group and group & {"sofa", "settee"} for group in groups("tools", "synonyms.txt"))
    return changed and index() != built()


@stale
def stale_index_hand_edited():
    # index/words.json knows sofa or settee though tools/synonyms.txt, which it is built from, doesn't: the next
    # build loses them.
    words = index()
    return ("sofa" in words or "settee" in words) and words != built()


@stale
def stale_synonyms_at_query_time():
    # find knows sofa though the index doesn't: synonyms applied by search.py, outside the index.
    import search

    return "sofa" not in index() and bool(search.find("sofa"))


print(json.dumps(out))
