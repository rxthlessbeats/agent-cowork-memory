"""The front desk's fine calculator: python3 desk.py DUE RETURNED PRICE, with dates as YYYY-MM-DD."""
import sys
from datetime import date
from decimal import Decimal

import library

if __name__ == "__main__":
    due, returned, price = sys.argv[1:4]
    print(library.fine(date.fromisoformat(due), date.fromisoformat(returned), Decimal(price)))
