"""The morning dunning run: python3 daily.py invoices.json [YYYY-MM-DD], for today when no date is given.

invoices.json is a list of invoices, with the amount as a string and the due date as YYYY-MM-DD.
"""
import json
import sys
from datetime import date
from decimal import Decimal

import dunning

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        invoices = [{**i, "amount": Decimal(i["amount"]), "due": date.fromisoformat(i["due"])} for i in json.load(f)]
    today = date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date.today()
    for invoice in invoices:
        step = dunning.next_step(invoice, today)
        if step:
            print(invoice["number"], step)
