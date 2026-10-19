"""The ticket office till: python3 till.py AGE [YYYY-MM-DD], for today when no date is given."""
import sys
from datetime import date

import skipass

if __name__ == "__main__":
    day = date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date.today()
    print(skipass.price(int(sys.argv[1]), day))
