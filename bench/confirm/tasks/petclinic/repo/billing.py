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
