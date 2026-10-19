import copy
import os

DEFAULTS = {
    "debug": False,
    "workers": 2,
    "db": {"host": "localhost", "port": 5432},
}
PREFIX = "MYAPP_"


def parse(value):
    if value.lower() in ("yes", "no", "true", "false"):
        return value.lower() in ("yes", "true")
    return int(value) if value.isdigit() else value


def load(environ=None):
    environ = os.environ if environ is None else environ
    config = copy.deepcopy(DEFAULTS)
    for name, value in environ.items():
        if not name.startswith(PREFIX):
            continue
        *parents, key = name[len(PREFIX):].lower().split(".")
        target = config
        for part in parents:
            target = target.get(part) if isinstance(target, dict) else None
        if not (isinstance(target, dict) and key in target and not isinstance(target[key], dict)):
            raise KeyError(f"unknown setting {name}")
        target[key] = parse(value)
    return config
