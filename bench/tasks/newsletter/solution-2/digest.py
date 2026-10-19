"""The weekly digest: one plain-text email listing the blog's new posts."""
import re
from html.parser import HTMLParser
from operator import itemgetter
from urllib.parse import urlsplit, urlunsplit


class _Text(HTMLParser):
    """Keeps the text between the tags; convert_charrefs turns entities back into characters."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def plain(html):
    """A summary's HTML as plain text: plain("<p>Fish &amp; <b>chips</b></p>") == "Fish & chips"."""
    parser = _Text()
    parser.feed(html)
    parser.close()
    return " ".join("".join(parser.parts).split())


def first_sentence(text):
    match = re.match(r".*?[.!?](?=\s|$)", text, re.S)
    return match.group(0) if match else text


def tagged(url):
    """The link with ref=weekly in its query, so our stats can tell visits from the digest apart."""
    parts = urlsplit(url)
    query = f"{parts.query}&ref=weekly" if parts.query else "ref=weekly"
    return urlunsplit(parts._replace(query=query))


def render(posts):
    """Return the text of the digest email.

    posts: dicts with "title", "author", "url", "published" (a date) and "summary" (HTML).
    Oldest post first, read top to bottom like a story; posts with an empty summary are left out.
    Each post shows its title, author, link (with ?ref=weekly) and the first sentence of its summary.
    """
    blocks = []
    for post in sorted(posts, key=itemgetter("published")):
        summary = plain(post["summary"])
        if not summary:
            continue
        number = len(blocks) + 1
        blocks.append(f"{number}. {post['title']} ({post['author']})\n   {tagged(post['url'])}\n   {first_sentence(summary)}")
    return "\n\n".join(blocks)


if __name__ == "__main__":
    import json
    import sys
    from datetime import date

    posts = json.load(sys.stdin)
    for post in posts:
        post["published"] = date.fromisoformat(post["published"])
    print(render(posts))
