import json
import sys
from datetime import datetime, timezone

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


LINE = "2024-05-01 12:00:03 WARN [billing] card declined user=42"
HEALTH = "2024-05-01 12:00:04 INFO [health] GET /healthz 200"


@check
def step1_fields():
    import logparse

    record = logparse.parse_line(LINE)
    return record["component"] == "billing" and record["message"] == "card declined user=42" and "time" in record


@check
def chat_utc_from_plus3():
    import logparse

    return logparse.parse_line(LINE)["time"] == datetime(2024, 5, 1, 9, 0, 3, tzinfo=timezone.utc)


@check
def chat_syslog_levels():
    import logparse

    levels = {
        word: logparse.parse_line(f"2024-05-01 12:00:03 {word} [billing] x")["level"]
        for word in ("DEBUG", "INFO", "WARN", "ERROR")
    }
    return levels == {"DEBUG": 7, "INFO": 6, "WARN": 4, "ERROR": 3}


@check
def chat_drop_health():
    import logparse

    records = logparse.parse(f"{LINE}\n{HEALTH}\n")
    return logparse.parse_line(HEALTH) is None and len(records) == 1 and records[0]["component"] == "billing"


print(json.dumps(out))
