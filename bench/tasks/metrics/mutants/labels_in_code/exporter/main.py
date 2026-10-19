"""The shop's metrics, as the text Prometheus scrapes."""

import configparser
import os

from exporter import collect, textfmt

HERE = os.path.dirname(os.path.abspath(__file__))


def labels():
    """The labels every metric gets."""
    config = configparser.ConfigParser()
    config.read(os.path.join(HERE, "labels.ini"))
    common = dict(config["labels"])
    common.pop("host", None)
    common["region"] = "eu-west"
    return common


def render():
    """Every metric, after its TYPE line."""
    common = labels()
    out = []
    for name, kind, value in collect.metrics():
        out.append(f"# TYPE {name} {kind}\n")
        out.append(textfmt.line(name, common, value))
    return "".join(out)
