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


DEFAULTS = {"debug": False, "workers": 2, "db": {"host": "localhost", "port": 5432}}


def load(env):
    import config

    return config.load(env)


@check
def step1_top_level():
    return str(load({"MYAPP_WORKERS": "4"})["workers"]) == "4" and load({}) == DEFAULTS


@check
def chat_dot_nested():
    db = load({"MYAPP_DB.PORT": "6000", "MYAPP_DB.HOST": "db1"})["db"]
    return str(db["port"]) == "6000" and db["host"] == "db1"


@check
def chat_yes_no():
    cfg = load({"MYAPP_DEBUG": "yes", "MYAPP_WORKERS": "8"})
    return (
        cfg["debug"] is True
        and type(cfg["workers"]) is int
        and cfg["workers"] == 8
        and load({"MYAPP_DEBUG": "no"})["debug"] is False
        and load({"MYAPP_DEBUG": "true"})["debug"] == "true"
    )


@check
def chat_unknown_raises():
    for env in ({"MYAPP_COLOR": "red"}, {"MYAPP_DB.USER": "x"}):
        try:
            load(env)
            return False
        except KeyError as err:
            if list(env)[0] not in str(err):
                return False
    return True


print(json.dumps(out))
