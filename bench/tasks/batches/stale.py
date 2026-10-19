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


def sizes(direction, n):
    """The sizes of the batches sync's export or import makes of n rows."""
    import sync

    return [len(b) for b in getattr(sync, f"{direction}_batches")([{"id": i} for i in range(n)])]


@stale
def stale_5000():
    # README.md and settings.BATCH_SIZE: batches of 5,000 rows.
    return 5000 in (sizes("export", 20000)[0], sizes("import", 20000)[0])


@stale
def stale_one_size():
    # One setting for export and import alike: both cut 20,000 rows into the same batches.
    return sizes("export", 20000) == sizes("import", 20000)


@stale
def stale_swapped():
    # The two sizes the wrong way round: export in batches of 2,750, import in batches of 7,500.
    return sizes("export", 20000)[0] == 2750 and sizes("import", 20000)[0] == 7500


@stale
def stale_empty_end():
    # README.md: a transfer always ends with an empty batch, even one of 100 rows.
    return any(sizes(d, 100)[-1:] == [0] for d in ("export", "import"))


print(json.dumps(out))
