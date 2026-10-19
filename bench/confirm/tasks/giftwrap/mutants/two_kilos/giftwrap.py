"""Gift wrapping at checkout."""

from settings import FREE_WRAP_FROM
from shop import total

MAX_WEIGHT = 2000  # grams: 2 kg, the most the scale on the wrapping table takes
FEE = 366  # cents for each wrapped item: paper, ribbon and tag
CARD_CHARACTERS = 42  # what the card printer fits


def clean_message(text):
    """The message with each run of whitespace turned into one space, and none at either end."""
    return " ".join(text.split())


def quote(items, message):
    wrapped = [item["sku"] for item in items if item["weight"] <= MAX_WEIGHT]
    fee = 0 if total(items) >= FREE_WRAP_FROM else FEE * len(wrapped)
    return {"wrapped": wrapped, "fee": fee, "message": clean_message(message)[:CARD_CHARACTERS]}
