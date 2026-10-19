"""Feature flags, from flags.ini: the section for the environment named in SHOP_ENV (live if unset), and
[DEFAULT] for any flag that section doesn't set."""

import configparser
import os

FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flags.ini")


def enabled(name):
    config = configparser.ConfigParser()
    config.read(FILE)
    return config.getboolean(os.environ.get("SHOP_ENV", "live"), name)
