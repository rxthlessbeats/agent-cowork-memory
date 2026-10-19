"""Send support tickets to the queue of the team that handles them."""
import re

# A ticket that mentions one of a team's words is for that team.
KEYWORDS = {
    "billing": ["invoice", "refund", "charge", "payment"],
    "sales": ["pricing", "quote", "upgrade", "discount"],
    "tech": ["error", "crash", "bug", "password"],
}
GENERAL = "general"
ONCALL = "oncall"  # priority 1 tickets skip the teams
PRECEDENCE = ("sales", "billing", "tech")  # who gets a subject that matches several teams; tech only when no other

# One case-insensitive, whole-word pattern per team.
PATTERNS = {team: re.compile(r"\b(?:%s)\b" % "|".join(map(re.escape, words)), re.I) for team, words in KEYWORDS.items()}


def teams(text):
    """The teams whose words appear in the text, ignoring case, in the order KEYWORDS lists them."""
    return [team for team, pattern in PATTERNS.items() if pattern.search(text)]


def route(ticket):
    """Return the queue for a ticket.

    ticket: a dict with "subject", "body", "email" and "priority" (1 is the most urgent, 4 the least).
    Priority 1 goes straight to the oncall queue. Otherwise only the subject counts (bodies are mostly
    quoted old emails): sales before billing before tech, or the general queue when no team's words appear.
    """
    if ticket["priority"] == 1:
        return ONCALL
    matched = teams(ticket["subject"])
    return next((team for team in PRECEDENCE if team in matched), GENERAL)


if __name__ == "__main__":
    import json
    import sys

    print(route(json.load(sys.stdin)))
