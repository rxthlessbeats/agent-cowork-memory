import json

HIDDEN = {"password", "token", "api_key"}


def redact(value):
    if isinstance(value, list):
        for v in value:
            redact(v)
    elif isinstance(value, dict):
        for key, inner in value.items():
            name = str(key).lower()
            if name in HIDDEN:
                value[key] = "[REDACTED]"
            elif name == "card_number":
                digits = str(inner)
                value[key] = "".join("*" if c.isdigit() else c for c in digits[:-4]) + digits[-4:]
            else:
                redact(inner)
    return value


def format_event(event):
    return json.dumps(redact(event), sort_keys=True)
