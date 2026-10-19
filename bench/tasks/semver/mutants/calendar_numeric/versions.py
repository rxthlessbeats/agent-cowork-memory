def parse(version):
    """Split a version like "1.4.2" into numbers."""
    return tuple(int(part) for part in version.split("."))


def rank(version):
    """Versions by their numbers; a hotfix above its plain version."""
    number, _, suffix = version.partition("-")
    return parse(number), suffix == "hotfix"


def latest(versions):
    """The newest version in the list, with a v in front for git."""
    return "v" + max(versions, key=rank)
