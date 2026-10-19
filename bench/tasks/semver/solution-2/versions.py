from functools import cmp_to_key


def parse(version):
    """Split a version like "1.4.2" into numbers."""
    return tuple(map(int, version.split(".")))


def compare(a, b):
    """-1, 0, or 1 as version a is older than, as new as, or newer than version b."""
    base_a, _, tag_a = a.partition("-")
    base_b, _, tag_b = b.partition("-")
    nums_a, nums_b = parse(base_a), parse(base_b)
    calendar_a, calendar_b = len(nums_a) == 2, len(nums_b) == 2
    if calendar_a != calendar_b:
        return -1 if calendar_a else 1  # old two-part calendar releases lose to every X.Y.Z
    if nums_a != nums_b:
        return -1 if nums_a < nums_b else 1
    return (tag_a == "hotfix") - (tag_b == "hotfix")  # a hotfix build beats its plain release


def latest(versions):
    """The newest version in the list, with a v in front: the release script hands it to git."""
    return "v" + max(versions, key=cmp_to_key(compare))
