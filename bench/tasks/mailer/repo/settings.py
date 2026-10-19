"""The mailer's settings, from the TOML files in config/."""

import os
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
# Read in this order: a value in a later file replaces the same value from an earlier one.
FILES = ("default.toml", "local.toml")


def load():
    settings = {}
    for name in FILES:
        path = os.path.join(HERE, "config", name)
        if os.path.exists(path):
            with open(path, "rb") as f:
                for table, values in tomllib.load(f).items():
                    settings.setdefault(table, {}).update(values)
    # A deployment can still pin the sender without touching the files.
    if os.environ.get("MAILER_FROM"):
        settings["mail"]["from"] = os.environ["MAILER_FROM"]
    return settings
