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


ITEMS = list(range(10))


@check
def step1_page_count():
    import pager

    return pager.page_count(10, 3) == 4 and pager.page_count(9, 3) == 3 and pager.page_count(0, 3) == 0


@check
def chat_one_based():
    import pager

    return pager.page(ITEMS, 1, 3) == [0, 1, 2] and pager.page(ITEMS, 4, 3) == [9]


@check
def chat_out_of_range():
    import pager

    return all(pager.page(ITEMS, n, 3) == [] for n in (0, -1, 5, 99))


print(json.dumps(out))
