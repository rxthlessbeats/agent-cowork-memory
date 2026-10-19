"""Receipt numbers for the shop's tills."""
import re
from datetime import date
from itertools import count


def parse(number):
    """Split a receipt number into its year and counter, as ints: parse("2026-00042") == (2026, 42)."""
    match = re.fullmatch(r"\s*(\d{4})-(\d+)\s*", number)
    if not match:
        raise ValueError(f"not a receipt number: {number!r}")
    return int(match[1]), int(match[2])


def financial_year(day):
    """The year the financial year holding `day` began. It starts on 1 April: 31 March 2027 is still 2026."""
    return day.year if day >= date(day.year, 4, 1) else day.year - 1


def next_number(last, today):
    """Return the number for a receipt issued on `today`.

    last: the number of the receipt before it, or None for the very first receipt.
    Numbers look like 2026-00042: the year the financial year began, then a 5-digit counter that
    starts again at 1 on 1 April and never has a 13 in it (after 12 comes 14, after 129 comes 140).
    """
    year = financial_year(today)
    start = 1
    if last is not None:
        last_year, last_counter = parse(last)
        if last_year == year:
            start = last_counter + 1
    counter = next(n for n in count(start) if "13" not in str(n))
    return f"{year}-{str(counter).zfill(5)}"


if __name__ == "__main__":
    import sys

    # python3 receipts.py [LAST_NUMBER]
    print(next_number(sys.argv[1] if len(sys.argv) > 1 else None, date.today()))
