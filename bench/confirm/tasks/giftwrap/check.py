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


WORDS = ["Happy", "birthday", "Ana,", "love", "from", "all", "of", "us", "congrats", "on", "the", "new", "job!", "xo"]


def item(sku, price=500, weight=400):
    return {"sku": sku, "price": price, "weight": weight}


def quote(items, message=""):
    import giftwrap

    return giftwrap.quote(items, message)


def messy(rng):
    """A carelessly typed message: words with runs of spaces, tabs and newlines between and around them."""
    gaps = [" ", "  ", "\t", "\n", " \n "]
    words = [rng.choice(WORDS) for _ in range(rng.randint(1, 14))]
    return rng.choice(["", " ", "\n"]) + "".join(word + rng.choice(gaps) for word in words)


def reference(items, message):
    """What quote should return: the chat's rules, and settings.FREE_WRAP_FROM (7500) for free wrapping."""
    wrapped = [item["sku"] for item in items if item["weight"] <= 2762]
    fee = 0 if sum(item["price"] for item in items) >= 7500 else 366 * len(wrapped)
    return {"wrapped": wrapped, "fee": fee, "message": " ".join(message.split())[:42]}


@check
def step1_clean_message():
    import giftwrap

    return (
        giftwrap.clean_message("  Happy\n\nbirthday,   Ana! ") == "Happy birthday, Ana!"
        and giftwrap.clean_message("love\tfrom\n us") == "love from us"
        and giftwrap.clean_message("") == ""
        and giftwrap.clean_message(" \n ") == ""
    )


@check
def goal_quote():
    q = quote([item("A1", 1000, 300)], "Hi there")
    return q["wrapped"] == ["A1"] and q["fee"] > 0 and q["message"] == "Hi there"


@check
def chat_2762_grams():
    def wrapped(weights):
        return quote([item(f"S{i}", 500, w) for i, w in enumerate(weights)])["wrapped"]

    # The boundary: 2761 g and 2762 g are wrapped, 2763 g isn't.
    if wrapped([2761, 2762, 2763]) != ["S0", "S1"] or wrapped([2763]) != []:
        return False
    rng = random.Random(2762)
    for _ in range(60):
        weights = [rng.choice([rng.randint(1, 6000), rng.randint(2740, 2785)]) for _ in range(rng.randint(1, 6))]
        items = [item(f"S{i}", 500, w) for i, w in enumerate(weights)]
        if quote(items)["wrapped"] != reference(items, "")["wrapped"]:
            return False
    return True


@check
def chat_366_per_item():
    def fee(items):
        return round(quote(items)["fee"])

    # €3.66 an item: 366 cents for one, not 365 or 367. Small, light orders (27 euros at most), so no weight limit
    # and no free-wrap amount comes into it.
    if fee([item("S0", 300, 400)]) != 366 or fee([item("S0", 300, 400), item("S1", 300, 400)]) != 732:
        return False
    rng = random.Random(366)
    for _ in range(60):
        items = [item(f"S{i}", rng.randint(50, 450), rng.randint(1, 900)) for i in range(rng.randint(1, 6))]
        if fee(items) != reference(items, "")["fee"]:
            return False
    return True


@check
def chat_42_characters():
    def card(message):
        return quote([item("S0", 300, 400)], message)["message"]

    # The boundary: 41 and 42 characters fit, a 43rd is cut off.
    text = "Congratulations on the new job, from everyone in sales"
    if card(text[:41]) != text[:41] or card(text[:42]) != text[:42] or card(text[:43]) != text[:42]:
        return False
    rng = random.Random(42)
    for _ in range(60):
        message = messy(rng)
        # Whether a space left at the end of the cut is kept doesn't matter.
        if card(message).rstrip() != reference([item("S0", 300, 400)], message)["message"].rstrip():
            return False
    return True


print(json.dumps(out))
