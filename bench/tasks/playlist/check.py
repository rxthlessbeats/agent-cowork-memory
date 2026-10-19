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


def track(title, artist, seconds):
    return {"title": title, "artist": artist, "seconds": seconds}


@check
def step1_length():
    import playlist

    lengths = [playlist.length(s) for s in (337, 9, 0, 600, 3600, 3725)]
    return lengths == ["5:37", "0:09", "0:00", "10:00", "1:00:00", "1:02:05"]


@check
def goal_build():
    import playlist

    tracks = [track("One", "Ann", 200), track("Two", "Bea", 200), track("Three", "Cal", 200)]
    return sorted(playlist.build(tracks, 60)) == ["One", "Three", "Two"] and len(playlist.build(tracks, 5)) < 3


@check
def chat_no_track_over_7_minutes():
    import playlist

    tracks = [track("Long", "Ann", 450), track("Fine", "Bea", 400), track("Short", "Cal", 200)]
    return sorted(playlist.build(tracks, 60)) == ["Fine", "Short"]


@check
def chat_two_per_artist():
    import playlist

    tracks = [track(f"Nina {i}", "Nina", 150) for i in range(5)] + [track("Otis", "Otis", 150)]
    titles = playlist.build(tracks, 60)
    return sum(t.startswith("Nina") for t in titles) == 2 and "Otis" in titles


@check
def changed_last_6_minutes_free():
    import playlist

    # 17 minutes of 2-minute tracks: 5 fit with 6 minutes kept free, 6 with the first plan's 4, 8 with none.
    tracks = [track(f"Song {i}", f"Artist {i}", 120) for i in range(10)]
    return len(playlist.build(tracks, 17)) == 5


print(json.dumps(out))
