"""The trade-in counter: python3 counter.py phones.txt

Each line of the file is one phone: its IMEI, price, the day it was bought (YYYY-MM-DD), battery health and
whether the screen is cracked (yes or no), separated by spaces.
"""
import sys
from datetime import date
from decimal import Decimal

import buyback


def read(path):
    """The phones listed in the file at `path`."""
    phones = []
    with open(path) as f:
        for line in f:
            if line.strip():
                imei, price, bought, battery, cracked = line.split()
                phones.append(
                    {
                        "imei": imei,
                        "price": Decimal(price),
                        "bought": date.fromisoformat(bought),
                        "battery": int(battery),
                        "cracked": cracked == "yes",
                    }
                )
    return phones


if __name__ == "__main__":
    for phone in read(sys.argv[1]):
        print(phone["imei"], buyback.offer(phone, date.today()))
