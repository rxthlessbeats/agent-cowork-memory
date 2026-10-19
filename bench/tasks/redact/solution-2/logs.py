import copy
import json

SECRET = {"password", "token", "api_key"}


def mask_card(number):
    """Every digit but the last 4 becomes *; separators stay as they are."""
    keep = 4
    out = []
    for ch in reversed(str(number)):
        if ch.isdigit():
            if keep:
                keep -= 1
            else:
                ch = "*"
        out.append(ch)
    return "".join(reversed(out))


def format_event(event):
    event = copy.deepcopy(event)  # never change the event the caller passed in
    stack = [event]
    while stack:
        node = stack.pop()
        if isinstance(node, (list, tuple)):
            stack.extend(node)
        elif isinstance(node, dict):
            for key, value in node.items():
                name = key.lower() if isinstance(key, str) else key
                if name in SECRET:
                    node[key] = "[REDACTED]"
                elif name == "card_number":
                    node[key] = mask_card(value)
                else:
                    stack.append(value)
    return json.dumps(event, sort_keys=True)
