import json

HIDDEN = {"password", "token", "api_key"}


def redact(value):
    if not isinstance(value, dict):
        return value
    out = {}
    for key, inner in value.items():
        name = str(key).lower()
        if name in HIDDEN:
            out[key] = "[REDACTED]"
        elif name == "card_number":
            digits = str(inner)
            out[key] = "".join("*" if c.isdigit() else c for c in digits[:-4]) + digits[-4:]
        else:
            out[key] = redact(inner)
    return out


def format_event(event):
    return json.dumps(redact(event), sort_keys=True)
