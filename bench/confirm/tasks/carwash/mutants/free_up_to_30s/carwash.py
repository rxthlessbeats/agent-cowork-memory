"""The self-service jet wash bays: the bay controller's session log, and charging customers' cards."""

from datetime import datetime

from config import MEMBER_DISCOUNT

PENCE_A_MINUTE = 15  # every started minute: the card terminal can only bill whole minutes
MOST_MINUTES = 22  # nobody pays for more: past that the jet runs for free, so nobody races the clock
FREE_UNDER = 30  # seconds or less: someone checking the lance, or a card tapped by mistake


def sessions(path):
    """Every session in the bay controller's log at path, one parsed line each."""
    with open(path) as log:
        return [parse_log(line) for line in log if line.strip()]


def parse_log(line):
    """A log line as (bay, card, seconds the jet ran): "B2 C-1042 14:05:10 14:12:41" -> ("B2", "C-1042", 451)."""
    bay, card, on, off = line.split()
    ran = datetime.strptime(off, "%H:%M:%S") - datetime.strptime(on, "%H:%M:%S")
    return bay, card, int(ran.total_seconds())


def charge(session):
    """What a session costs the customer's card, in pence."""
    seconds = session["seconds"]
    if seconds <= FREE_UNDER:
        return 0
    minutes = min(-(-seconds // 60), MOST_MINUTES)
    pence = minutes * PENCE_A_MINUTE
    if session["member"]:
        pence = round(pence * (100 - MEMBER_DISCOUNT) / 100)
    return pence
