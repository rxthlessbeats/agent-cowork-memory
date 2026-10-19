import json
import random
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


# The jackpot rule looks at the day: checks of the other rules play on a Saturday, far from Tuesday and the days
# a slip would hit instead (Thursday, or Monday and Wednesday for a weekday off by one).
SATURDAY = date(2026, 11, 7)
CARD = 250  # hall.CARD_PRICE


def reference(day, cards, calls):
    """What payout should return: the chat's rules (32 calls, turn 4's), and hall.JACKPOT (50000)."""
    won = calls <= 32 and day.weekday() != 1
    return {"prize": cards * CARD * 44 // 100, "jackpot": 50000 if won else 0}


def payout(day=SATURDAY, cards=100, calls=50):
    import bingo

    return bingo.payout({"day": day, "cards": cards, "calls": calls})


def any_day(rng):
    return date(2026, 1, 1) + timedelta(days=rng.randint(0, 364))


@check
def step1_call_name():
    import bingo

    names = [bingo.call_name(n) for n in (1, 7, 15, 16, 30, 31, 45, 46, 60, 61, 75)]
    return names == ["B-1", "B-7", "B-15", "I-16", "I-30", "N-31", "N-45", "G-46", "G-60", "O-61", "O-75"]


@check
def goal_payout():
    quick, slow = payout(calls=26), payout(calls=70)
    return quick["prize"] > 0 and quick["jackpot"] > 0 and slow["jackpot"] == 0 and payout(cards=200)["prize"] > slow["prize"]


@check
def chat_prize_44():
    def prize(cards):
        return round(payout(SATURDAY, cards, 50)["prize"])

    # 44% of the card sales: 100 cards sell for 25000, so 11000, not 10750 (43%) or 11250 (45%).
    if prize(100) != 11000 or prize(1) != 110:
        return False
    rng = random.Random(44)
    for _ in range(60):
        cards = rng.randint(1, 600)
        if prize(cards) != reference(SATURDAY, cards, 50)["prize"]:
            return False
    return True


@check
def changed_jackpot_32():
    def won(calls):
        return payout(SATURDAY, 100, calls)["jackpot"] > 0

    # The boundary: 31 and 32 calls win the jackpot, 33 doesn't, and neither does the first plan's 34.
    if not (won(31) and won(32) and not won(33) and not won(34)):
        return False
    rng = random.Random(32)
    for _ in range(60):
        calls = rng.choice([rng.randint(24, 75), rng.randint(29, 36)])
        if won(calls) != (reference(SATURDAY, 100, calls)["jackpot"] > 0):
            return False
    return True


@check
def chat_no_jackpot_tuesday():
    def jackpot(day, calls=26):
        return payout(day, 100, calls)["jackpot"]

    monday, tuesday, wednesday = date(2026, 11, 2), date(2026, 11, 3), date(2026, 11, 4)
    # The boundary: Monday and Wednesday pay the jackpot, Tuesday doesn't, though it still pays the prize.
    if not (jackpot(monday) > 0 and jackpot(tuesday) == 0 and jackpot(wednesday) > 0):
        return False
    if round(payout(tuesday, 100, 26)["prize"]) != round(payout(monday, 100, 26)["prize"]):
        return False
    rng = random.Random(2)
    for _ in range(60):
        day, calls = any_day(rng), rng.randint(24, 30)
        if (jackpot(day, calls) > 0) != (reference(day, 100, calls)["jackpot"] > 0):
            return False
    return True


print(json.dumps(out))
