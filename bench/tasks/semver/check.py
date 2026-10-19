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


def latest(*versions):
    """latest() without any v prefix, so only the ordering is judged."""
    import versions as module

    return module.latest(list(versions)).removeprefix("v")


@check
def step1_parse():
    import versions

    return versions.parse("1.10.2") == (1, 10, 2) and versions.parse("0.0.1") == (0, 0, 1)


@check
def goal_numeric_order():
    return latest("1.9.0", "1.10.0", "1.2.3") == "1.10.0"


@check
def chat_hotfix_above():
    return (
        latest("1.10.0", "1.10.0-hotfix", "1.9.0") == "1.10.0-hotfix"
        and latest("1.10.0-hotfix", "1.10.0") == "1.10.0-hotfix"
        and latest("1.10.0-hotfix", "1.10.1") == "1.10.1"
    )


@check
def chat_calendar_below():
    return latest("2023.4", "1.10.0", "1.9.0") == "1.10.0"


@check
def chat_v_prefix():
    import versions

    return versions.latest(["1.2.3"]) == "v1.2.3" and versions.latest(["1.9.0", "1.10.0"]) == "v1.10.0"


print(json.dumps(out))
