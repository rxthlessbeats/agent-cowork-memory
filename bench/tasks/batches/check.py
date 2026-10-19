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


def rows(n):
    return [{"id": i} for i in range(n)]


def batches(direction, n):
    """The batches sync's export or import makes of n rows, as lists."""
    import sync

    return [list(b) for b in getattr(sync, f"{direction}_batches")(rows(n))]


def joined(direction, n):
    return [row for batch in batches(direction, n) for row in batch]


@check
def step1_chunks():
    import sync

    return [list(c) for c in sync.chunks(list(range(7)), 3)] == [[0, 1, 2], [3, 4, 5], [6]]


@check
def goal_all_rows_in_order():
    return all(len(batches(d, 12000)) > 1 and joined(d, 12000) == rows(12000) for d in ("export", "import"))


@check
def chat_export_7500():
    return [len(b) for b in batches("export", 20000) if b] == [7500, 7500, 5000]


@check
def chat_import_2750():
    return [len(b) for b in batches("import", 6000) if b] == [2750, 2750, 500]


@check
def chat_no_empty_batch():
    # Nothing to send, and exact multiples of both the right size and the README's 5,000.
    cases = [("export", 0), ("export", 15000), ("import", 0), ("import", 5500)]
    return all(all(batches(d, n)) and joined(d, n) == rows(n) for d, n in cases)


print(json.dumps(out))
