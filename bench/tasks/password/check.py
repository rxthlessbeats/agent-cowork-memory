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


GOOD = "Sunny-day-42x"  # meets every rule, and the usual upper/lower/symbol ones too


@check
def step1_min_length():
    import password

    return not password.is_valid("Ab-c-12xy") and password.is_valid("Ab-cd-12xy") and password.is_valid(GOOD)


@check
def chat_two_digits():
    import password

    return not password.is_valid("Sunny-day-4x!") and password.is_valid(GOOD)


@check
def chat_no_company_name():
    import password

    return not password.is_valid("My-BrightWELL-42x") and password.is_valid("My-Bright-Well-42x")


@check
def chat_no_trailing_digit():
    import password

    return not password.is_valid("Sunny-day-x42") and password.is_valid(GOOD)


print(json.dumps(out))
