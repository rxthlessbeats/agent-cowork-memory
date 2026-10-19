"""Receipt numbers for the shop's tills."""

YEAR_STARTS = 4  # the financial year starts on 1 April


def parse(number):
    """Split a receipt number into its year and counter: parse("2026-0042") == (2026, 42)."""
    year, counter = number.split("-")
    return int(year), int(counter)


def next_number(last, today):
    """Return the number for a receipt issued on `today`.

    last: the number of the receipt before it, or None for the very first receipt.
    Numbers look like 2026-0042: the year the financial year began, then a counter that starts
    again at 1 each financial year and skips every number with a 13 in it.
    """
    year = today.year if today.month >= YEAR_STARTS else today.year - 1
    counter = parse(last)[1] if last and parse(last)[0] == year else 0
    counter += 1
    while "13" in str(counter):
        counter += 1
    return f"{year}-{counter:04d}"


if __name__ == "__main__":
    import sys
    from datetime import date

    # python3 receipts.py [LAST_NUMBER]
    print(next_number(sys.argv[1] if len(sys.argv) > 1 else None, date.today()))
