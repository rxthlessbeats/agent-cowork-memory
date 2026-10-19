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
