"""Receipt numbers for the shop's tills."""


def next_number(last, today):
    """Return the number for a receipt issued on `today`.

    last: the number of the receipt before it, or None for the very first receipt.
    Numbers look like 2026-0042: the year, then a counter that starts again at 1 each year.
    """
    raise NotImplementedError


if __name__ == "__main__":
    import sys
    from datetime import date

    # python3 receipts.py [LAST_NUMBER]
    print(next_number(sys.argv[1] if len(sys.argv) > 1 else None, date.today()))
