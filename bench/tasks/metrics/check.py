import configparser
import json
import os
import re
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}

LINE = re.compile(r"^(\w+)\{(.*)\} (\S+)$")
LABEL = re.compile(r'(\w+)="((?:[^"\\]|\\.)*)"')
WANT = {"service": "shop", "region": "eu-west"}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def metrics(text):
    """{metric name: (its labels, its value)} for each metric line of the text format."""
    found = {}
    for line in text.splitlines():
        if line and not line.startswith("#"):
            name, labels, value = LINE.match(line).groups()
            found[name] = (dict(LABEL.findall(labels)), value)
    return found


@check
def step1_escape():
    from exporter import textfmt

    return (
        textfmt.escape('say "hi"') == 'say \\"hi\\"'
        and textfmt.escape("C:\\temp") == "C:\\\\temp"
        and textfmt.escape("two\nlines") == "two\\nlines"
        and textfmt.escape('\\"') == '\\\\\\"'
        and textfmt.escape("eu-west") == "eu-west"
    )


@check
def goal_region_label():
    from exporter import main

    return metrics(main.render()) == {
        "shop_up": (WANT, "1"),
        "shop_orders_total": (WANT, "1027"),
        "shop_open_carts": (WANT, "12"),
    }


@check
def found_labels_ini():
    # exporter/main.py reads the labels from labels.ini next to it, in exporter/: labels.example.ini at the top of
    # the repo is never read.
    config = configparser.ConfigParser()
    config.read(os.path.join(repo, "exporter", "labels.ini"))
    return dict(config["labels"]) == WANT


print(json.dumps(out))
