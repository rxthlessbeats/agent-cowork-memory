"""Search over the docs: find(query) gives the documents that have every word of the query."""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def _index():
    """Each word, with the names of the documents that have it."""
    with open(os.path.join(HERE, "index", "words.json")) as f:
        return json.load(f)


def find(query):
    """query: words separated by spaces, in any case ("Couch" finds what "couch" does: the index is lowercase).
    Returns the names of the matching documents, sorted."""
    index = _index()
    words = query.lower().split()
    if not words:
        return []
    found = set(index.get(words[0], []))
    for word in words[1:]:
        found &= set(index.get(word, []))
    return sorted(found)
