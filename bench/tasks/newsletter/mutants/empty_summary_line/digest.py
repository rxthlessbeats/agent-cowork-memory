"""The weekly digest: one plain-text email listing the blog's new posts."""
import re
from html import unescape


def plain(html):
    """A summary's HTML as plain text: plain("<p>Fish &amp; <b>chips</b></p>") == "Fish & chips"."""
    return unescape(re.sub(r"<[^>]*>", "", html)).strip()


def render(posts):
    """Return the text of the digest email.

    posts: dicts with "title", "author", "url", "published" (a date) and "summary" (HTML).
    The oldest post comes first. Each post shows its title, author, link (tagged ?ref=weekly for our
    stats) and the first sentence of its summary, skipping empty summaries.
    """
    entries = []
    for post in sorted(posts, key=lambda p: p["published"]):
        entry = f"{post['title']}, by {post['author']}\n{post['url']}?ref=weekly"
        summary = plain(post["summary"])
        if summary:
            entry += "\n" + re.split(r"(?<=[.!?])\s", summary, maxsplit=1)[0]
        entries.append(entry)
    return "\n\n".join(entries)


if __name__ == "__main__":
    import json
    import sys
    from datetime import date

    posts = json.load(sys.stdin)
    for post in posts:
        post["published"] = date.fromisoformat(post["published"])
    print(render(posts))
