"""Disk space alerts for the ops channel."""
from bisect import bisect_right

THRESHOLDS = (83, 96)  # percent used: a warning from the first, critical from the second
LEVELS = ("ok", "warning", "critical")


def parse(line):
    """A reading from the disk agent, like "web-1 /var 91.5" or "web-1 /var 91.5%", as (host, mount, percent used)."""
    host, mount, percent = line.split()
    return host, mount, float(percent.removesuffix("%"))


def level(history):
    """How full a disk is: "ok", "warning" or "critical", from its percent-used readings, oldest first.

    The lowest of the last three readings decides, so a single spike never alerts.
    """
    settled = sorted(history[-3:])[0]
    return LEVELS[bisect_right(THRESHOLDS, settled)]


def message(host, mount, history):
    """The line to post in the ops channel about this disk, or None when it is ok.

    Host first, since the on-call bot only picks up lines that start with it: "web-1:/var WARNING 85%",
    with the latest reading rounded to a whole percent.
    """
    status = level(history)
    if status == "ok":
        return None
    return "{}:{} {} {:.0f}%".format(host, mount, status.upper(), history[-1])


if __name__ == "__main__":
    import sys

    host, mount, percent = parse(sys.argv[1])
    print(message(host, mount, [percent]))
