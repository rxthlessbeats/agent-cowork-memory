"""Helpers for the docs site's markdown pages."""
import re

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def headings(markdown):
    """(level, text) for each ATX heading in the document."""
    found = []
    for line in markdown.splitlines():
        match = HEADING.match(line)
        if match:
            found.append((len(match.group(1)), match.group(2)))
    return found


def slug(text):
    """GitHub-style anchor for a heading: lowercase, punctuation dropped, spaces to hyphens."""
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"\s+", "-", text)
