import json
import random
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


ADULT = 2450  # fares.ADULT


def reference(departure, adults, vehicle):
    """What ticket should return, times as minutes: the chat's rules, and harbour.BOARDING_MINUTES (30)."""
    lane = None if vehicle is None else "long" if vehicle > 4631 else "car"
    price = adults * (ADULT + 82) + {None: 0, "car": 3900, "long": 6500}[lane]
    departs = minutes(departure)
    return {"price": price, "lane": lane, "check_in": departs - 64, "boarding": departs - 30}


def ticket(departure="10:50", adults=1, vehicle=None):
    import tickets

    return tickets.ticket({"departure": departure, "adults": adults, "vehicle": vehicle})


def minutes(hhmm):
    hours, mins = hhmm.split(":")
    return int(hours) * 60 + int(mins)


def clock(total):
    return f"{total // 60:02d}:{total % 60:02d}"


@check
def step1_minutes():
    import tickets

    return (
        tickets.to_minutes("07:45") == 465
        and tickets.to_minutes("00:00") == 0
        and tickets.to_minutes("23:59") == 1439
        and tickets.to_clock(465) == "07:45"
        and tickets.to_clock(0) == "00:00"
        and tickets.to_clock(605) == "10:05"
        and tickets.to_clock(1439) == "23:59"
    )


@check
def goal_ticket():
    foot = ticket(adults=2)
    car = ticket(adults=2, vehicle=4000)
    return (
        foot["lane"] is None
        and car["lane"] == "car"
        and car["price"] > foot["price"] >= 2 * ADULT
        and minutes(foot["check_in"]) < minutes("10:50")
        and minutes(foot["boarding"]) < minutes("10:50")
    )


@check
def chat_long_over_4631():
    def lane(mm):
        return ticket(vehicle=mm)["lane"]

    # The boundary: 4630 mm and 4631 mm are the car lane, 4632 mm is the long one.
    if [lane(4630), lane(4631), lane(4632)] != ["car", "car", "long"]:
        return False
    rng = random.Random(4631)
    for _ in range(60):
        mm = rng.choice([rng.randint(3000, 7000), rng.randint(4600, 4660)])
        if lane(mm) != reference("10:50", 1, mm)["lane"]:
            return False
    return True


@check
def chat_check_in_64():
    def closes(departure):
        return minutes(ticket(departure=departure)["check_in"])

    # 64 minutes before: 09:46 for a 10:50 sailing, not 09:47 (63) or 09:45 (65).
    if closes("10:50") != minutes("09:46") or closes("06:40") != minutes("05:36"):
        return False
    rng = random.Random(64)
    for _ in range(60):
        departure = clock(rng.randint(5 * 60, 23 * 60 + 59))
        if closes(departure) != reference(departure, 1, None)["check_in"]:
            return False
    return True


@check
def chat_harbour_fee_82():
    def price(adults, departure="10:50"):
        return round(ticket(departure=departure, adults=adults)["price"])

    # €0.82 a passenger: 2532 for one foot passenger, not 2531 or 2533.
    if price(1) != ADULT + 82 or price(3) != 3 * (ADULT + 82):
        return False
    rng = random.Random(82)
    for _ in range(60):
        adults, departure = rng.randint(1, 12), clock(rng.randint(5 * 60, 23 * 60 + 59))
        if price(adults, departure) != reference(departure, adults, None)["price"]:
            return False
    return True


print(json.dumps(out))
