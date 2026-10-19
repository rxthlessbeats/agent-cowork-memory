import json
import sys
from datetime import date, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


TODAY = date(2026, 3, 28)  # a Saturday


def name(day):
    return f"backup-{day.isoformat()}.tar.gz"


def ago(days):
    return name(TODAY - timedelta(days=days))


def kept():
    """What keep leaves of one nightly backup for each of the last 400 days."""
    import retention

    names = [ago(n) for n in range(399, -1, -1)]
    result = set(retention.keep(names, TODAY))
    assert result <= set(names)
    return result


@check
def step1_made_on():
    import retention

    return (
        retention.made_on("backup-2026-03-02.tar.gz") == date(2026, 3, 2)
        and retention.made_on("backup-2025-12-31.tar.gz") == date(2025, 12, 31)
    )


@check
def goal_thins_out():
    k = kept()
    return {ago(0), ago(1), ago(2)} <= k and len(k) < 60


@check
def chat1_ten_days_of_dailies():
    k = kept()
    return ago(8) in k and ago(9) in k and ago(11) not in k  # a Friday, a Thursday and a Tuesday


@check
def chat1_wednesday_weeklies():
    k = kept()
    wednesdays = {name(date(2026, 3, 11)), name(date(2026, 3, 4))}
    sundays = {name(date(2026, 3, 15)), name(date(2026, 3, 8))}
    return wednesdays <= k and not sundays & k


@check
def chat2_oldest_kept():
    k = kept()
    return ago(399) in k and ago(398) not in k


@check
def chat2_first_of_month_for_six_months():
    k = kept()
    recent = {name(date(2025, 11, 1)), name(date(2025, 12, 1)), name(date(2026, 1, 1))}
    older = {name(date(2025, 8, 1)), name(date(2025, 5, 1))}
    return recent <= k and not older & k


print(json.dumps(out))
