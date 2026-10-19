import re
import unicodedata

MAX = 40


def slugify(title):
    plain = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")


def cut(slug, limit):
    return slug if len(slug) <= limit else slug[: limit + 1].rsplit("-", 1)[0]


def unique_slug(title, taken):
    base = cut(slugify(title), MAX)
    slug = base
    n = 2
    while slug in taken:
        slug = f"{base}-{n}"
        n += 1
    return slug
