import copy
import os

DEFAULTS = {
    "debug": False,
    "workers": 2,
    "db": {"host": "localhost", "port": 5432},
}

PREFIX = "MYAPP_"
WORDS = {"yes": True, "no": False}  # how ops writes booleans; "true" and "false" stay strings


def convert(text):
    if text in WORDS:
        return WORDS[text]
    return int(text) if text.isascii() and text.isdigit() else text


def paths(tree, prefix=()):
    """Every setting's key path in tree, like ("db", "port")."""
    for key, value in tree.items():
        if isinstance(value, dict):
            yield from paths(value, (*prefix, key))
        else:
            yield (*prefix, key)


def load(environ=None):
    environ = os.environ if environ is None else environ
    config = copy.deepcopy(DEFAULTS)
    # Nested keys use a dot, which our orchestrator allows: MYAPP_DB.PORT sets db.port.
    known = {".".join(path).upper(): path for path in paths(config)}
    for name, text in environ.items():
        if not name.startswith(PREFIX):
            continue
        path = known.get(name[len(PREFIX) :].upper())
        if path is None:
            raise KeyError(f"{name} matches no setting (a typo?)")
        *parents, leaf = path
        node = config
        for key in parents:
            node = node[key]
        node[leaf] = convert(text)
    return config
