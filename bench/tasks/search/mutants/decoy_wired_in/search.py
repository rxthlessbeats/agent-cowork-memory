"""Search over the docs: find(query) gives the documents that have every word of the query, or of its synonyms."""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def _index():
    """Each word, with the names of the documents that have it."""
    with open(os.path.join(HERE, "index", "words.json")) as f:
        return json.load(f)


def _synonyms():
    """Each word in synonyms.txt, with every word of its group."""
    groups = {}
    with open(os.path.join(HERE, "synonyms.txt")) as f:
        for line in f:
            words = {word.strip().lower() for word in line.split("#")[0].split(",")} - {""}
            for word in words:
                groups[word] = words
    return groups


def find(query):
    """query: words separated by spaces, in any case. Returns the names of the matching documents, sorted."""
    index = _index()
    synonyms = _synonyms()
    found = None
    for word in query.lower().split():
        docs = set().union(*(index.get(w, []) for w in synonyms.get(word, {word})))
        found = docs if found is None else found & docs
    return sorted(found or [])
