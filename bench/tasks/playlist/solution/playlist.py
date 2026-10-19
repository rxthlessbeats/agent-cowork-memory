"""The café's music library.

Each track is a dict with a title, an artist and its length in seconds.
"""

LIBRARY = [
    {"title": "Blue in Green", "artist": "Miles Davis", "seconds": 337},
    {"title": "So What", "artist": "Miles Davis", "seconds": 562},
    {"title": "Naima", "artist": "John Coltrane", "seconds": 261},
    {"title": "Cantaloupe Island", "artist": "Herbie Hancock", "seconds": 330},
    {"title": "Take Five", "artist": "Dave Brubeck Quartet", "seconds": 324},
    {"title": "Moanin'", "artist": "Art Blakey", "seconds": 575},
]


def total_seconds(tracks):
    return sum(t["seconds"] for t in tracks)


def by_artist(tracks, artist):
    """Titles of the tracks by this artist, in library order."""
    return [t["title"] for t in tracks if t["artist"] == artist]


def length(seconds):
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


LONGEST_TRACK = 7 * 60
PER_ARTIST = 2
KEEP_FREE = 6 * 60  # seconds at the end of the shift, for the closing announcement


def build(tracks, minutes):
    room = minutes * 60 - KEEP_FREE
    titles, plays = [], {}
    for t in tracks:
        if t["seconds"] > min(room, LONGEST_TRACK) or plays.get(t["artist"], 0) >= PER_ARTIST:
            continue
        titles.append(t["title"])
        plays[t["artist"]] = plays.get(t["artist"], 0) + 1
        room -= t["seconds"]
    return titles
