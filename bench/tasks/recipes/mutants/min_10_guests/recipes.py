"""Recipes cooked in the staff canteen.

A recipe says how many people it serves and maps each ingredient to an
amount and a unit: "g" for grams or "ml" for millilitres.
"""
import math

RECIPES = {
    "pancakes": {
        "serves": 4,
        "ingredients": {"flour": (250, "g"), "milk": (500, "ml"), "butter": (30, "g"), "salt": (2, "g")},
    },
    "tomato soup": {
        "serves": 6,
        "ingredients": {"tomatoes": (1200, "g"), "stock": (750, "ml"), "onion": (150, "g"), "pepper": (1, "g")},
    },
}


def ingredient_names(recipe):
    return sorted(recipe["ingredients"])


def shopping_list(recipes):
    """Total amount of each ingredient over several recipes, keyed by (name, unit)."""
    totals = {}
    for recipe in recipes:
        for name, (amount, unit) in recipe["ingredients"].items():
            totals[(name, unit)] = totals.get((name, unit), 0) + amount
    return totals


def per_person(recipe):
    return {name: (amount / recipe["serves"], unit) for name, (amount, unit) in recipe["ingredients"].items()}


UNSCALED = ("salt", "pepper")
STEP = 25
MIN_GUESTS = 10


def scale(recipe, guests):
    guests = max(guests, MIN_GUESTS)
    scaled = {}
    for name, (amount, unit) in recipe["ingredients"].items():
        if name not in UNSCALED:
            amount = math.ceil(amount * guests / recipe["serves"] / STEP) * STEP
        scaled[name] = (amount, unit)
    return scaled
