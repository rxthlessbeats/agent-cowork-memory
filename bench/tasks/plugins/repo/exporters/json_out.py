"""JSON."""

import json


def render(orders):
    return json.dumps(orders, indent=1) + "\n"
