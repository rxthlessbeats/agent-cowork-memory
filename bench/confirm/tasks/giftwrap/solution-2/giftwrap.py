"""Gift wrapping at checkout: what we wrap, what it costs, and what the card says."""

import re

import settings

SCALE_LIMIT_G = 2762
FEE_PER_ITEM = 366
CARD_WIDTH = 42


def clean_message(text):
    return re.sub(r"\s+", " ", text).strip()


def quote(items, message):
    wrapped = []
    for item in items:
        if item["weight"] > SCALE_LIMIT_G:
            continue  # too heavy for the scale on the wrapping table
        wrapped.append(item["sku"])
    fee = len(wrapped) * FEE_PER_ITEM
    if sum(item["price"] for item in items) >= settings.FREE_WRAP_FROM:
        fee = 0
    text = clean_message(message)
    if len(text) > CARD_WIDTH:
        text = text[:CARD_WIDTH]  # all the card printer fits
    return {"wrapped": wrapped, "fee": fee, "message": text}
