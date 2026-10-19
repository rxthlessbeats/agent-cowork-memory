"""The café's music library.

Each track is a dict with a title, an artist and its length in seconds.
"""
from collections import Counter

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
    """A track length as text: length(337) is "5:37", length(9) is "0:09", length(3725) is "1:02:05"."""
    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}:{secs:02d}"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}"


MAX_TRACK_SECONDS = 7 * 60  # longer tracks are never played
MAX_PLAYS_PER_ARTIST = 2
CLOSING_MINUTES = 6  # left free at the end of the shift for the closing announcement (was 4)


def build(tracks, minutes):
    """Titles in play order: tracks in the given order that fit in the shift minus the closing minutes."""
    budget = (minutes - CLOSING_MINUTES) * 60
    used, plays, titles = 0, Counter(), []
    for t in tracks:
        if t["seconds"] > MAX_TRACK_SECONDS or plays[t["artist"]] == MAX_PLAYS_PER_ARTIST:
            continue
        if used + t["seconds"] > budget:
            continue
        used += t["seconds"]
        plays[t["artist"]] += 1
        titles.append(t["title"])
    return titles
