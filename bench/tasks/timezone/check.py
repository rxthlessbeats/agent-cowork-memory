import json
import re
import sys
from datetime import datetime, timedelta, timezone

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


UTC = timezone.utc


def shown(*args, tz=UTC):
    import times

    return times.fmt(datetime(*args, tzinfo=tz))


@check
def step1_aware_starts():
    import times

    noon = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
    starts = [times.parse_time(t) for t in ("2026-07-01T12:00", "2026-07-01T12:00:00Z", "2026-07-01T14:00+02:00")]
    return all(s.tzinfo is not None and s == noon for s in starts)


@check
def goal_fmt():
    # Mid-January, when Lisbon is on UTC: the date and the clock read the same in either zone.
    text = shown(2026, 1, 15, 9, 5)
    return "2026" in text and re.search(r"\b0?9:05\b", text)


@check
def chat_lisbon_time():
    # Lisbon is UTC+1 in summer, so noon UTC (and 14:00 at +02:00) is 13:00 there; in winter it is on UTC.
    return (
        re.search(r"\b13:00\b", shown(2026, 7, 1, 12, 0))
        and re.search(r"\b13:00\b", shown(2026, 7, 1, 14, 0, tz=timezone(timedelta(hours=2))))
        and re.search(r"\b20:30\b", shown(2026, 12, 10, 20, 30))
    )


@check
def chat_dotted_date():
    # Winter middays, when Lisbon is on UTC: whichever zone is used, the date can't move.
    return re.search(r"\b31\.12\.2026\b", shown(2026, 12, 31, 12, 0)) and re.search(
        r"\b0?4\.0?3\.2026\b", shown(2026, 3, 4, 10, 15)
    )


print(json.dumps(out))
