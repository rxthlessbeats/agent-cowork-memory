"""Recipes cooked in the staff canteen.

A recipe says how many people it serves and maps each ingredient to an
amount and a unit: "g" for grams or "ml" for millilitres.
"""

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
    """The ingredients for one person: each amount divided by the people the recipe serves, units unchanged."""
    serves = recipe["serves"]
    result = {}
    for name, (amount, unit) in recipe["ingredients"].items():
        result[name] = (amount / serves, unit)
    return result


FIXED = {"salt", "pepper"}  # never scaled: kept exactly as in the recipe
STEP = 25  # the kitchen's jugs and scales are marked in 25s
SMALLEST_BATCH = 12  # guests (10 before the bigger pans)


def scale(recipe, guests):
    """The ingredients for this many guests (at least SMALLEST_BATCH), each rounded up to a multiple of STEP."""
    guests = max(guests, SMALLEST_BATCH)
    serves = recipe["serves"]
    scaled = {}
    for name, (amount, unit) in recipe["ingredients"].items():
        if name not in FIXED:
            # Ceiling division keeps exact multiples as they are: 1225 g stays 1225 g.
            amount = -(-amount * guests // (serves * STEP)) * STEP
        scaled[name] = (amount, unit)
    return scaled
