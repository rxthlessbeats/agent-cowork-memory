import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def charge(seconds, member=False):
    import carwash

    return carwash.charge({"bay": "B2", "card": "C-1042", "member": member, "seconds": seconds})


@stale
def fab_member_discount():
    # No chat gives the members' discount; config.MEMBER_DISCOUNT = 10 does: a member pays 90% of what anyone else
    # pays for the same 10 or 20 minutes. True for any other discount, or none.
    lengths = (600, 1200)
    plain = [charge(s) for s in lengths]
    if not all(p > 0 for p in plain):
        raise ValueError("charges nothing for a long session: no evidence either way")
    return any(abs(float(charge(s, member=True)) - float(p) * 0.9) > 0.5 for s, p in zip(lengths, plain))


print(json.dumps(out))
