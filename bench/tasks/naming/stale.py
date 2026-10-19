import json
import sys
from datetime import date

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@stale
def stale_client_name():
    # Chat 1's client part, which chat 2 replaced with the padded client number: the name in capitals, ACMECORP.
    import naming

    return "ACMECORP" in naming.export_name(42, "sales", date(2026, 3, 2))


print(json.dumps(out))
