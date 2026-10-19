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


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def ini_labels(*path):
    config = configparser.ConfigParser()
    config.read(os.path.join(repo, *path))
    return dict(config["labels"])


@stale
def stale_example_edited():
    # The region label in labels.example.ini, which the exporter never reads, and not in exporter/labels.ini, which it
    # does. (The example kept in step with labels.ini is documentation, not a mistake.)
    example = ini_labels("labels.example.ini")
    return example.get("region") == "eu-west" and ini_labels("exporter", "labels.ini").get("region") != "eu-west"


@stale
def stale_labels_not_from_ini():
    # render() puts labels on the metrics that exporter/labels.ini doesn't say: they come from code, or another file.
    from exporter import main

    live = ini_labels("exporter", "labels.ini")
    lines = [line for line in main.render().splitlines() if line and not line.startswith("#")]
    return any(dict(LABEL.findall(LINE.match(line).group(2))) != live for line in lines)


print(json.dumps(out))
