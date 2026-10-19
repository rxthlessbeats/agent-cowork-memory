"""Send support tickets to the queue of the team that handles them."""
import re

# A ticket that mentions one of a team's words is for that team.
KEYWORDS = {
    "billing": ["invoice", "refund", "charge", "payment"],
    "sales": ["pricing", "quote", "upgrade", "discount"],
    "tech": ["error", "crash", "bug", "password"],
}
GENERAL = "general"
ONCALL = "oncall"


def teams(text):
    """The teams whose words appear in text, ignoring case, in the order KEYWORDS lists them."""
    found = set(re.findall(r"\w+", text.lower()))
    return [team for team, words in KEYWORDS.items() if found.intersection(words)]


def route(ticket):
    """Return the queue for a ticket.

    ticket: a dict with "subject", "body", "email" and "priority" (1 is the most urgent, 4 the least).
    Priority 1 tickets go to on-call. The rest go to the team with the most of its words in the subject
    (the body is ignored), or to the general queue when none match.
    """
    if ticket["priority"] == 1:
        return ONCALL
    words = re.findall(r"\w+", ticket["subject"].lower())
    hits = {team: sum(word in team_words for word in words) for team, team_words in KEYWORDS.items()}
    best = max(hits, key=hits.get)
    return best if hits[best] else GENERAL


if __name__ == "__main__":
    import json
    import sys

    print(route(json.load(sys.stdin)))
