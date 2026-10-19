# Jet wash charges

The self-service jet wash bays log every session but charge nobody yet. Add `charge(session)` to carwash.py: what a session costs the customer's card, in pence. A session is a dict with "bay", "card", "member" (True for members) and "seconds", how long the jet ran. Members get their discount.
