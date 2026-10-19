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


@check
def step1_parse_percent():
    import alerts

    return alerts.parse("web-1 /var 91.5%") == ("web-1", "/var", 91.5) and alerts.parse("db-2 /data 7") == ("db-2", "/data", 7)


@check
def goal_levels():
    import alerts

    return (
        alerts.level([99, 99, 99]) == "critical"
        and alerts.level([10, 10, 10]) == "ok"
        and alerts.message("web-1", "/var", [10, 10, 10]) is None
        and "web-1" in alerts.message("web-1", "/var", [99, 99, 99])
    )


@check
def chat1_83_and_96():
    import alerts

    def steady(percent):
        return alerts.level([percent] * 3)

    return steady(82.9) == "ok" and steady(83) == "warning" and steady(95.9) == "warning" and steady(96) == "critical"


@check
def chat1_lowest_of_last_three():
    import alerts

    return alerts.level([50, 99, 99]) == "ok" and alerts.level([20, 99, 99, 99]) == "critical"


@check
def chat2_host_first():
    import alerts

    # A warning and a critical at the usual thresholds too, and the latest and the lowest reading round alike.
    return (
        alerts.message("web-1", "/var", [88.2, 88.4, 88.1]) == "web-1:/var WARNING 88%"
        and alerts.message("db-2", "/data", [97.2, 97.1, 97.4]) == "db-2:/data CRITICAL 97%"
    )


print(json.dumps(out))
