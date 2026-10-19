import re
import unicodedata

MAX = 40


def slugify(title):
    plain = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")


def cut(slug, limit):
    return slug if len(slug) <= limit else slug[: limit + 1].rsplit("-", 1)[0]


def unique_slug(title, exists):
    """exists(slug) says whether a post already uses that slug."""
    base = slugify(title)
    slug = cut(base, MAX)
    n = 2
    while exists(slug):
        suffix = f"-{n}"
        slug = cut(base, MAX - len(suffix)) + suffix
        n += 1
    return slug
