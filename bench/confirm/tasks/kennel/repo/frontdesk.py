"""The front desk's bill printer: python3 frontdesk.py CHECKIN COLLECTED DOG [DOG ...]

Times look like 2026-05-04T15:00; a dog on medication is written NAME+meds, like Rex+meds.
"""

import sys
from datetime import datetime

import kennel


def main(argv):
    checkin, collected = datetime.fromisoformat(argv[0]), datetime.fromisoformat(argv[1])
    dogs = [{"name": arg.removesuffix("+meds"), "meds": arg.endswith("+meds")} for arg in argv[2:]]
    cents = kennel.bill(dogs, checkin, collected)
    names = ", ".join(dog["name"] for dog in dogs)
    print(f"{names}: {checkin:%d %b %H:%M} to {collected:%d %b %H:%M}, {cents // 100}.{cents % 100:02d}")


if __name__ == "__main__":
    main(sys.argv[1:])
