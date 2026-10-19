"""Bills for the pet clinic.

An invoice is a dict: "number", "owner", "pet", "issued" (a date) and "balance" (a Decimal: what is still unpaid).
"""

from datetime import date
from decimal import Decimal

LATE_FEE = Decimal("4.50")  # added to the balance on every reminder letter

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
    """How many days have passed since the invoice was issued: 0 on the day itself.

    >>> days_unpaid({"number": "A-1", "issued": date(2026, 3, 1)}, date(2026, 3, 31))
    30
    """
    if invoice["issued"] > today:
        raise ValueError("issued after today")
    return today.toordinal() - invoice["issued"].toordinal()


def reminders(invoices, today):
    """The reminder letters to send today, as (invoice number, amount to ask for) pairs, in the invoices' order.

    Chased: invoices unpaid for 62 days or more (the longest two months), with at least 1.61 owed (what a letter
    costs to send). Never on a Monday, which is surgery day. The amount is the balance plus LATE_FEE.
    """
    letters = []
    if today.isoweekday() == 1:
        return letters
    for invoice in invoices:
        if invoice["balance"] < Decimal("1.61") or days_unpaid(invoice, today) < 62:
            continue
        letters.append((invoice["number"], invoice["balance"] + LATE_FEE))
    return letters
