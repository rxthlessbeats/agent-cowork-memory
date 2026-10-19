import json
import random
import sys
from datetime import date, timedelta
from decimal import Decimal
from fractions import Fraction

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


TODAY = date(2026, 6, 15)


def phone(price="500.00", days=10, battery=90, cracked=False):
    """A phone bought `days` days before TODAY."""
    return {
        "imei": "490154203237518",
        "price": Decimal(price),
        "bought": TODAY - timedelta(days=days),
        "battery": battery,
        "cracked": cracked,
    }


def offered(**kw):
    """offer for phone(**kw) on TODAY in cents, whatever number type it returns, or None when it isn't taken."""
    import buyback

    amount = buyback.offer(phone(**kw), TODAY)
    return None if amount is None else round(Decimal(str(amount)) * 100)


def reference(days, battery, cracked, whole):
    """The refurbisher's rules, for a phone that would get `whole` cents with its screen whole: what offer should give."""
    if battery < 62 or days > 91:
        return None
    return Fraction(whole) * Fraction(60, 100) if cracked else whole


def near(got, want):
    """Equal to within a cent, whichever way the folder rounds."""
    return abs(got - want) <= 1


def price(rng):
    return f"{rng.randint(100, 1500)}.{rng.randint(0, 99):02d}"


@check
def step1_valid_imei():
    import buyback

    return (
        buyback.valid_imei("490154203237518")
        and buyback.valid_imei("356938035643809")
        and not buyback.valid_imei("490154203237519")
        and not buyback.valid_imei("49015420323751")
        and not buyback.valid_imei("49015420323751a")
    )


@check
def goal_offers_for_phones():
    cheap, dear = offered(price="500.00"), offered(price="1000.00")
    return cheap is not None and dear is not None and 0 < cheap < dear


@check
def changed_battery_62():
    # Taken from 62% battery health, which turn 4 brought down from 80%; at 61%, not taken.
    if [offered(battery=b) is None for b in (61, 62, 63)] != [True, False, False]:
        return False
    rng = random.Random(6262)
    for _ in range(60):
        days, battery, cracked = rng.randint(0, 25), rng.randint(30, 100), rng.random() < 0.3
        got = offered(price=price(rng), days=days, battery=battery, cracked=cracked)
        if (got is None) != (reference(days, battery, cracked, 1) is None):
            return False
    return True


@check
def chat_bought_within_91_days():
    # Bought 91 days ago is fine; 92 days ago is too old.
    if [offered(days=d) is None for d in (90, 91, 92)] != [False, False, True]:
        return False
    rng = random.Random(9191)
    for _ in range(60):
        days, battery, cracked = rng.randint(0, 200), rng.randint(85, 100), rng.random() < 0.3
        got = offered(price=price(rng), days=days, battery=battery, cracked=cracked)
        if (got is None) != (reference(days, battery, cracked, 1) is None):
            return False
    return True


@check
def chat_cracked_40_off():
    # A cracked screen takes 40% off whatever the phone would get whole: 39% or 41% off is out by over a cent here.
    whole, cracked = offered(price="1000.00"), offered(price="1000.00", cracked=True)
    if not whole or whole <= 0 or cracked is None or not near(cracked, reference(10, 90, True, whole)):
        return False
    rng = random.Random(4040)
    for _ in range(60):
        cost, days, battery = f"{20 * rng.randint(5, 75)}.00", rng.randint(0, 25), rng.randint(85, 100)
        whole = offered(price=cost, days=days, battery=battery)
        got = offered(price=cost, days=days, battery=battery, cracked=True)
        if not whole or whole <= 0 or got is None or not near(got, reference(days, battery, True, whole)):
            return False
    return True


print(json.dumps(out))
