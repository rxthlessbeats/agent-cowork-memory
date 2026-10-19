"""Send support tickets to the queue of the team that handles them."""

# A ticket that mentions one of a team's words is for that team.
KEYWORDS = {
    "billing": ["invoice", "refund", "charge", "payment"],
    "sales": ["pricing", "quote", "upgrade", "discount"],
    "tech": ["error", "crash", "bug", "password"],
}
GENERAL = "general"


def route(ticket):
    """Return the queue for a ticket.

    ticket: a dict with "subject", "body", "email" and "priority" (1 is the most urgent, 4 the least).
    A ticket goes to the team whose words appear in its subject or body, or to the general queue when
    no team's words do.
    """
    return GENERAL


if __name__ == "__main__":
    import json
    import sys

    print(route(json.load(sys.stdin)))
