"""Search over the docs: find(query) gives the documents that have every word of the query."""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def _index():
    """Each word, with the names of the documents that have it."""
    with open(os.path.join(HERE, "index", "words.json")) as f:
        return json.load(f)


def find(query):
    """query: words separated by spaces. Returns the names of the matching documents, sorted."""
    index = _index()
    found = None
    for word in query.split():
        docs = set(index.get(word, []))
        found = docs if found is None else found & docs
    return sorted(found or [])
