import copy

DEFAULTS = {
    "debug": False,
    "workers": 2,
    "db": {"host": "localhost", "port": 5432},
}


def load(environ=None):
    return copy.deepcopy(DEFAULTS)
