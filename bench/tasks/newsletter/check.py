import json
import sys
from datetime import date

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def post(title, day, summary="<p>A short read.</p>"):
    return {
        "title": title,
        "author": "Ana Silva",
        "url": "https://blog.example/" + title.lower().replace(" ", "-"),
        "published": date(2026, 3, day),
        "summary": summary,
    }


def render(*posts):
    import digest

    return digest.render(list(posts))


@check
def step1_plain():
    import digest

    return digest.plain("<p>Fish &amp; <b>chips</b></p>") == "Fish & chips"


@check
def goal_lists_posts():
    posts = [post("Green tea", 2), post("Black tea", 4)]
    text = render(*posts)
    return all(p["title"] in text and p["url"] in text for p in posts) and "A short read" in text and "<p>" not in text


@check
def chat1_oldest_first():
    text = render(post("Oolong", 3), post("Matcha", 1), post("Sencha", 5))
    return text.index("Matcha") < text.index("Oolong") < text.index("Sencha")


@check
def chat1_ref_weekly():
    return "https://blog.example/green-tea?ref=weekly" in render(post("Green tea", 2))


@check
def chat2_first_sentence():
    text = render(post("Green tea", 2, "<p>Steep it cool. Then wait three minutes.</p>"))
    return "Steep it cool." in text and "three minutes" not in text


@check
def chat2_skip_empty_summary():
    text = render(post("Green tea", 2), post("Photo walk", 3, ""))
    return "Green tea" in text and "Photo walk" not in text and "photo-walk" not in text


print(json.dumps(out))
