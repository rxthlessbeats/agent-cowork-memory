import json

HIDDEN = {"password", "token", "api_key", "card_number"}


def redact(value):
    if isinstance(value, list):
        return [redact(v) for v in value]
    if not isinstance(value, dict):
        return value
    out = {}
    for key, inner in value.items():
        name = str(key).lower()
        if name in HIDDEN:
            out[key] = "[REDACTED]"
        else:
            out[key] = redact(inner)
    return out


def format_event(event):
    return json.dumps(redact(event), sort_keys=True)
