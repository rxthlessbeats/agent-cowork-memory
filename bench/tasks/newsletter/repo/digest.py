"""The weekly digest: one plain-text email listing the blog's new posts."""


def render(posts):
    """Return the text of the digest email.

    posts: dicts with "title", "author", "url", "published" (a date) and "summary" (HTML).
    The newest post comes first. Each post shows its title, author, link and summary.
    """
    raise NotImplementedError


if __name__ == "__main__":
    import json
    import sys
    from datetime import date

    posts = json.load(sys.stdin)
    for post in posts:
        post["published"] = date.fromisoformat(post["published"])
    print(render(posts))
