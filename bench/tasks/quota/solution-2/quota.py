"""Storage quota warnings for the account page."""
import math
from fractions import Fraction

GB = 1024**3
WARN_AT = Fraction(88, 100)  # users get a warning once they have used this share of their quota
MIN_FREE = 1 * GB  # anyone with less than this left gets one too, whatever their share
COMPANY = 1024 * GB  # quotas of 1 TB or more are company accounts: their admins get a report, not a warning


def percent(used, limit):
    """How much of the quota is used, as a percentage, so percent(GB, 4 * GB) == 25.0.

    A limit of 0 means the user has no quota: 0.0.
    """
    if limit == 0:
        return 0.0
    return float(Fraction(used) * 100 / Fraction(limit))


def warning(used, limit):
    """Return the warning to show a user, or None when they are not close to their quota.

    used: the bytes they store; limit: their quota, in bytes.
    """
    if limit <= 0 or limit >= COMPANY:
        return None
    share = Fraction(used) / Fraction(limit)  # exact, so the shown percentage rounds up only when it should
    if share < WARN_AT and limit - used >= MIN_FREE:
        return None
    return f"Your storage is {math.ceil(share * 100)}% full. Free up some space before uploads start failing."


if __name__ == "__main__":
    import sys

    # python3 quota.py USED_GB LIMIT_GB
    print(warning(float(sys.argv[1]) * GB, float(sys.argv[2]) * GB))
