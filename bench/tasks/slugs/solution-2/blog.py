import re
import unicodedata

LIMIT = 40  # characters, suffix included


def slugify(title):
    plain = "".join(c for c in unicodedata.normalize("NFKD", title) if not unicodedata.combining(c))
    return "-".join(re.findall(r"[a-z0-9]+", plain.lower()))


def fit(words, room):
    """The leading whole words that fit in room characters, joined by hyphens."""
    kept = []
    for word in words:
        if len("-".join(kept + [word])) > room:
            break
        kept.append(word)
    return "-".join(kept) or words[0][:room]  # a single over-long word can only be cut


def unique_slug(title, taken):
    words = slugify(title).split("-")
    slug = fit(words, LIMIT)
    n = 1
    while slug in taken:
        n += 1
        suffix = f"-{n}"
        slug = fit(words, LIMIT - len(suffix)) + suffix
    return slug
