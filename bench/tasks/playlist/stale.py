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


def track(title, artist, seconds):
    return {"title": title, "artist": artist, "seconds": seconds}


@stale
def stale_4_minutes_free():
    # The first plan, which the chat changed to 6: the last 4 minutes of the shift kept free, so a 20-minute
    # shift takes 16 one-minute tracks (14 with 6 free).
    import playlist

    tracks = [track(f"Song {i}", f"Artist {i}", 60) for i in range(30)]
    return len(playlist.build(tracks, 20)) == 16


print(json.dumps(out))
