"""Helpers for the docs site's markdown pages."""
import re

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
ANCHOR_PREFIX = "sec-"  # the docs site's renderer puts this before every heading anchor


def headings(markdown):
    """(level, text) for each ATX heading in the document, skipping fenced code (``` or ~~~, with or without a
    language tag)."""
    found = []
    fence = None  # the opening fence while inside fenced code
    for line in markdown.splitlines():
        marker = FENCE.match(line)
        if fence:
            # A fence closes on the same character, at least as long as the one that opened it.
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence):
                fence = None
            continue
        if marker:
            fence = marker.group(1)
            continue
        match = HEADING.match(line)
        if match:
            found.append((len(match.group(1)), match.group(2)))
    return found


def slug(text):
    """GitHub-style anchor for a heading: lowercase, punctuation dropped, spaces to hyphens."""
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"\s+", "-", text)


def toc(markdown):
    """The table of contents: a **Contents** line, a blank line, then a nested list linking each heading, drafts
    left out."""
    entries = [(level, text) for level, text in headings(markdown) if not text.endswith("(draft)")]
    top = min((level for level, _ in entries), default=1)
    lines = [f"{'  ' * (level - top)}- [{text}](#{ANCHOR_PREFIX}{slug(text)})" for level, text in entries]
    return "\n".join(["**Contents**", "", *lines])
