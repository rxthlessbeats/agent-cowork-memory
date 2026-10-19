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


TUESDAY = date(2025, 2, 4)
WEDNESDAY = date(2025, 2, 5)


def purchase(total, day=WEDNESDAY, member="M-1"):
    return {"member": member, "day": day, "total": total}


@check
def step1_spent():
    import loyalty

    purchases = [purchase(1000), purchase(500, member="M-2"), purchase(250)]
    return (
        loyalty.spent(purchases, "M-1") == 1250
        and loyalty.spent(purchases, "M-9") == 0
        and loyalty.spent([], "M-1") == 0
    )


@check
def goal_points():
    import loyalty

    return 0 < loyalty.points_for(purchase(5000)) < loyalty.points_for(purchase(10000))


@check
def chat_point_per_full_2_50():
    import loyalty

    return [loyalty.points_for(purchase(total)) for total in (1999, 2500, 1249)] == [7, 10, 4]


@check
def chat_nothing_under_10():
    import loyalty

    return loyalty.points_for(purchase(999)) == 0 and loyalty.points_for(purchase(1000)) > 0


@check
def chat_tuesday_double():
    import loyalty

    wednesday = loyalty.points_for(purchase(5000))
    return wednesday > 0 and loyalty.points_for(purchase(5000, TUESDAY)) == 2 * wednesday


print(json.dumps(out))
