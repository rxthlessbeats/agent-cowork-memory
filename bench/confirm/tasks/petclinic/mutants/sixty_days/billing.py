"""Bills for the pet clinic.

An invoice is a dict: "number", "owner", "pet", "issued" (a date) and "balance" (a Decimal: what is still unpaid).
"""

from datetime import date
from decimal import Decimal

LATE_FEE = Decimal("4.50")  # added to the balance on every reminder letter
CHASE_AFTER_DAYS = 60  # our terms give owners two months
MIN_BALANCE = Decimal("1.61")  # what a letter costs us to send
MONDAY = 0  # date.weekday(): surgery day, so no letters

INVOICES = [
    {"number": "A-1041", "owner": "Mia Novak", "pet": "Biscuit", "issued": date(2026, 1, 12), "balance": Decimal("86.40")},
    {"number": "A-1042", "owner": "Tom Reyes", "pet": "Pepper", "issued": date(2026, 1, 19), "balance": Decimal("0.00")},
    {"number": "A-1057", "owner": "Mia Novak", "pet": "Biscuit", "issued": date(2026, 2, 3), "balance": Decimal("12.20")},
    {"number": "A-1063", "owner": "Ines Duarte", "pet": "Juno", "issued": date(2026, 2, 21), "balance": Decimal("212.75")},
    {"number": "A-1070", "owner": "Sam Okoye", "pet": "Rufus", "issued": date(2026, 3, 9), "balance": Decimal("38.00")},
]


def total_owed(invoices, owner):
    """What an owner still owes across all their invoices."""
    total = Decimal("0.00")
    for inv in invoices:
        if inv["owner"] == owner:
            total += inv["balance"]
    return total


def days_unpaid(invoice, today):
    """How many days have passed since the invoice was issued: 0 on the day itself."""
    days = (today - invoice["issued"]).days
    if days < 0:
        raise ValueError(f"invoice {invoice['number']} was issued after {today}")
    return days


def reminders(invoices, today):
    """The reminder letters to send today, as (invoice number, balance plus the late fee) pairs."""
    if today.weekday() == MONDAY:
        return []
    return [
        (i["number"], i["balance"] + LATE_FEE)
        for i in invoices
        if days_unpaid(i, today) >= CHASE_AFTER_DAYS and i["balance"] >= MIN_BALANCE
    ]
