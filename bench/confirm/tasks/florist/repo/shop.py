"""The shop's settings."""

from datetime import time

OPENS = time(8, 30)
CLOSES = time(18, 0)
SAME_DAY_CUTOFF = time(14, 0)  # an order placed before this goes out the same day; a later one the next day
