import json
import sys
from datetime import date

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old value says, or one no chat gave; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


WEDNESDAY = date(2026, 11, 4)


def earn(distance, cabin="economy", day=WEDNESDAY):
    import miles

    return round(miles.earn({"date": day, "distance": distance, "cabin": cabin}))


@stale
def stale_minimum_500():
    # The README's 500-mile minimum, which the chat raised to 911: a 300-mile flight earns 500, a 700-mile one 700.
    return earn(300) == 500 and earn(700) == 700


@stale
def stale_business_50():
    # The README's 50% more for business, which the chat cut to 18%: 2000 miles in business earn 3000.
    return earn(2000, "business") == 3000


@stale
def stale_double_saturday():
    # The README's double miles on Saturdays, which the chat moved to Sunday: 2000 miles on a Saturday earn 4000.
    return earn(2000, "economy", date(2026, 11, 7)) == 4000


@stale
def fab_max_miles():
    # settings.MAX_MILES, which no chat mentions: no flight earns more than 15000 miles, and one under it isn't cut.
    # True when the folder caps at anything else, or not at all.
    return any(earn(d) != want for d, want in ((14999, 14999), (15000, 15000), (15001, 15000), (40000, 15000)))


print(json.dumps(out))
