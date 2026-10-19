import json


def format_event(event):
    return json.dumps(event, sort_keys=True)
