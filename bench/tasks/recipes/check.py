import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def recipe(serves, **ingredients):
    return {"serves": serves, "ingredients": ingredients}


@check
def step1_per_person():
    import recipes

    result = recipes.per_person(recipe(4, flour=(250, "g"), milk=(500, "ml")))
    flour, flour_unit = result["flour"]
    milk, milk_unit = result["milk"]
    return (
        sorted(result) == ["flour", "milk"]
        and abs(flour - 62.5) < 1e-9
        and abs(milk - 125) < 1e-9
        and (flour_unit, milk_unit) == ("g", "ml")
    )


@check
def goal_scale():
    import recipes

    result = recipes.scale(recipe(4, flour=(200, "g"), milk=(400, "ml")), 24)
    return tuple(result["flour"]) == (1200, "g") and tuple(result["milk"]) == (2400, "ml")


@check
def chat_round_up_to_25():
    import recipes

    # Unrounded: 1360 g and 840 ml.
    result = recipes.scale(recipe(4, flour=(340, "g"), milk=(210, "ml")), 16)
    return tuple(result["flour"]) == (1375, "g") and tuple(result["milk"]) == (850, "ml")


@check
def chat_salt_and_pepper_fixed():
    import recipes

    soup = recipe(4, flour=(200, "g"), salt=(3, "g"), pepper=(1, "g"))
    twenty, forty = recipes.scale(soup, 20), recipes.scale(soup, 40)
    return twenty["salt"] == forty["salt"] and twenty["pepper"] == forty["pepper"] and twenty["flour"] != forty["flour"]


@check
def changed_at_least_12_guests():
    import recipes

    # 125 g a head: 12 guests is 1500 g; the first plan's minimum of 10 would give 1250 g for 3 guests.
    batch = recipe(4, flour=(500, "g"))
    return recipes.scale(batch, 3)["flour"][0] == 1500 and recipes.scale(batch, 11)["flour"][0] == 1500


print(json.dumps(out))
