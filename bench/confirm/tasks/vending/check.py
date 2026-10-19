import json
import random
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


NOW = datetime(2026, 3, 5, 14, 0)


def machine(slots=((8, 10),), coins=100, seen=0, door=None):
    """A machine at NOW: slots as (count, capacity), last seen `seen` minutes ago, door open `door` minutes (None: shut)."""
    return {
        "id": "VM-9",
        "slots": [{"code": f"A{i + 1}", "product": "Cola", "count": n, "capacity": cap} for i, (n, cap) in enumerate(slots)],
        "coins": coins,
        "last_seen": NOW - timedelta(minutes=seen),
        "door_opened": None if door is None else NOW - timedelta(minutes=door),
    }


def alerts(**kw):
    import vending

    return set(vending.alerts(machine(**kw), NOW))


@check
def step1_fill_percent():
    import vending

    def pct(count, capacity):
        return vending.fill_percent({"code": "A1", "product": "Cola", "count": count, "capacity": capacity})

    return pct(3, 8) == 37 and pct(2, 3) == 66 and pct(0, 12) == 0 and pct(12, 12) == 100


@check
def goal_alerts():
    # A healthy machine has no alerts; an empty slot, an overflowing coin box and ten hours' silence each have one.
    return alerts() == set() and {"low_stock", "coins_full", "offline"} <= alerts(slots=((0, 10),), coins=5000, seen=600)


@check
def chat_low_under_26_percent():
    def low(*slots):
        return "low_stock" in alerts(slots=slots)

    # 25 of 100 is low; exactly 26% (26 of 100, 13 of 50) and 27% aren't. One low slot is enough.
    edges = [low((25, 100)), not low((26, 100)), not low((27, 100)), low((12, 50)), not low((13, 50))]
    edges.append(low((10, 10), (1, 8)))
    rng = random.Random(2601)
    same = []
    for _ in range(80):
        slots = []
        for _ in range(rng.randint(1, 3)):
            capacity = rng.randint(4, 60)
            slots.append((rng.randint(0, capacity), capacity))
        same.append(low(*slots) == any(n * 100 < 26 * cap for n, cap in slots))
    return all(edges) and all(same)


@check
def chat_coins_full_from_810():
    def full(coins):
        return "coins_full" in alerts(coins=coins)

    # 810 coins is full; 809 isn't. The box holds about 900, which is no longer the line.
    edges = [not full(809), full(810), full(811)]
    rng = random.Random(8101)
    same = [full(c) == (c >= 810) for c in (rng.randint(500, 1100) for _ in range(60))]
    return all(edges) and all(same)


@check
def chat_offline_after_48_minutes():
    def offline(minutes):
        return "offline" in alerts(seen=minutes)

    # Last seen 48 minutes ago is still online; 49 minutes ago is offline.
    edges = [not offline(47), not offline(48), offline(49)]
    rng = random.Random(4801)
    same = [offline(m) == (m > 48) for m in (rng.randint(0, 150) for _ in range(60))]
    return all(edges) and all(same)


print(json.dumps(out))
