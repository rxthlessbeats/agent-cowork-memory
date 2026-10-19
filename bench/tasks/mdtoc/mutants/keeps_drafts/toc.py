"""Helpers for the docs site's markdown pages."""
import re

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def headings(markdown):
    """(level, text) for each ATX heading in the document, skipping fenced code."""
    found = []
    fenced = False
    for line in markdown.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        match = HEADING.match(line)
        if match and not fenced:
            found.append((len(match.group(1)), match.group(2)))
    return found


def slug(text):
    """GitHub-style anchor for a heading: lowercase, punctuation dropped, spaces to hyphens."""
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"\s+", "-", text)


def toc(markdown):
    lines = ["**Contents**", ""]
    for level, text in headings(markdown):
        lines.append(f"{'  ' * (level - 1)}- [{text}](#sec-{slug(text)})")
    return "\n".join(lines)
