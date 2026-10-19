import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def logged(event):
    import logs

    return json.loads(logs.format_event(event))


@check
def step1_redact():
    return logged({"Password": "hunter2", "TOKEN": "t", "user": "ana"}) == {
        "Password": "[REDACTED]",
        "TOKEN": "[REDACTED]",
        "user": "ana",
    }


@check
def chat_api_key():
    return logged({"api_key": "k1", "user": "ana"}) == {"api_key": "[REDACTED]", "user": "ana"}


@check
def chat_nested():
    return logged({"auth": {"token": "t"}, "items": [{"password": "p"}, "plain"]}) == {
        "auth": {"token": "[REDACTED]"},
        "items": [{"password": "[REDACTED]"}, "plain"],
    }


@check
def chat_card_last4():
    return logged({"card_number": "4111111111114242"})["card_number"] == "************4242"


print(json.dumps(out))
