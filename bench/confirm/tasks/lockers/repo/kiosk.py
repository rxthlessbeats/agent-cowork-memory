"""The collection kiosk: python3 kiosk.py SIZE DROPPED COLLECTED, with times like 2026-05-05T09:30."""

import sys
from datetime import datetime

import lockers


def main(argv):
    size, dropped, collected = argv[0], datetime.fromisoformat(argv[1]), datetime.fromisoformat(argv[2])
    if size not in lockers.SIZES:
        raise SystemExit(f"size must be one of {', '.join(lockers.SIZES)}")
    print(lockers.receipt(size, dropped, collected))


if __name__ == "__main__":
    main(sys.argv[1:])
