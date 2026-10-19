"""Prints the tax for everyone in a payroll export: python3 export.py payroll.tsv

Each line of the export is a name, an age and a year's income, separated by tabs.
"""
import sys

from taxbands import parse_amount, tax


def read(path):
    """The (name, age, income) of everyone in the export at `path`."""
    people = []
    with open(path) as f:
        for row in f:
            if row.strip():
                name, age, income = row.rstrip("\n").split("\t")
                people.append((name, int(age), parse_amount(income)))
    return people


if __name__ == "__main__":
    for name, age, income in read(sys.argv[1]):
        print(name, tax(income, age))
