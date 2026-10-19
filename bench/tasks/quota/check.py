import json
import re
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def warn(used_gb, limit_gb):
    import quota

    return quota.warning(used_gb * quota.GB, limit_gb * quota.GB)


@check
def step1_percent():
    import quota

    return quota.percent(quota.GB, 4 * quota.GB) == 25 and quota.percent(5 * quota.GB, 0) == 0


@check
def goal_warns_near_quota():
    message = warn(99, 100)
    return isinstance(message, str) and message.strip() != "" and warn(10, 100) is None


@check
def chat1_warn_from_88():
    return warn(87, 100) is None and warn(89, 100) is not None


@check
def chat1_percent_rounded_up():
    message = warn(90.2, 100)
    return re.search(r"\b91 ?%", message) and not re.search(r"\b90(\.\d+)? ?%", message)


@check
def chat2_warn_under_1gb_free():
    return warn(3.1, 4) is not None and warn(2, 4) is None


@check
def chat2_no_warnings_from_1tb():
    return warn(1946, 2048) is None and warn(475, 500) is not None


print(json.dumps(out))
