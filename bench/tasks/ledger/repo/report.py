"""Prints the monthly report: each ledger entry, then the balance."""

from decimal import Decimal

from ledger import fmt, parse_amount

ENTRIES = [
    ("Opening balance", "18420.5"),
    ("Rent", "-2150"),
    ("Card sales", "6237.125"),
    ("Refund #1182", "-45.995"),
]


def main():
    total = Decimal(0)
    for name, text in ENTRIES:
        amount = parse_amount(text)
        total += amount
        print(f"{name:<20}{fmt(amount):>14}")
    print(f"{'Balance':<20}{fmt(total):>14}")


if __name__ == "__main__":
    main()
