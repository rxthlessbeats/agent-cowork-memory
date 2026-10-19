import json
import sys
from datetime import date

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


MON, NEXT_MON = date(2026, 3, 2), date(2026, 3, 9)


@check
def step1_skip_weekends():
    import workdays

    return workdays.workdays(MON, NEXT_MON) == 5 and workdays.workdays(MON, date(2026, 3, 16)) == 10


@check
def chat_end_counts_not_start():
    import workdays

    sun_to_mon = workdays.workdays(date(2026, 3, 8), NEXT_MON)
    fri_to_sat = workdays.workdays(date(2026, 3, 6), date(2026, 3, 7))
    return sun_to_mon == 1 and fri_to_sat == 0


@check
def chat_christmas_closure():
    import workdays

    # Saturday to Sunday, so which end counts makes no difference: only 21-23 Dec 2026 are open.
    return workdays.workdays(date(2026, 12, 19), date(2027, 1, 3)) == 3


@check
def chat_negative():
    import workdays

    return workdays.workdays(NEXT_MON, MON) == -5


print(json.dumps(out))
