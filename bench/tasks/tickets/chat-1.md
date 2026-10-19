Let's do TASK.md in two steps.

Step 1: add `teams(text)` to routing.py. It returns the teams whose words appear in the text, ignoring case, in the order KEYWORDS lists them, so `teams("Refund after the CRASH") == ["billing", "tech"]`. Leave `route` alone for now.

Step 2, for later: the routing in `route`. Only the subject counts: ignore the body, whatever the docstring says; it's mostly quoted old emails. And when a subject matches more than one team, sales gets the ticket first, then billing; tech only gets tickets that match no other team.

Do step 1 only for now, then stop. I'll come back for step 2.
