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


def route(subject, body="", priority=3):
    import routing

    return routing.route({"subject": subject, "body": body, "email": "sam@customer.example", "priority": priority})


@check
def step1_teams():
    import routing

    return routing.teams("Refund after the CRASH") == ["billing", "tech"] and routing.teams("Hello there") == []


@check
def goal_routes_by_keyword():
    return route("Refund please") == "billing" and route("App crash on start") == "tech" and route("Hello") == "general"


@check
def chat1_subject_only():
    return route("Question", "I would like a refund") == "general" and route("Refund", "Thanks") == "billing"


@check
def chat1_sales_then_billing_then_tech():
    # Billing has more words in the first subject, and KEYWORDS lists billing first and tech last.
    return (
        route("Refund and invoice for the upgrade") == "sales"
        and route("Invoice error") == "billing"
        and route("Crash after the upgrade") == "sales"
    )


@check
def chat2_priority1_oncall():
    return (
        route("Refund", priority=1) == "oncall"
        and route("Hello", priority=1) == "oncall"
        and route("Refund", priority=2) == "billing"
    )


print(json.dumps(out))
