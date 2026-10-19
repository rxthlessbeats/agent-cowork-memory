"""Disk space alerts for the ops channel."""

WARNING = 83
CRITICAL = 96


def parse(line):
    """A reading from the disk agent, like "web-1 /var 91.5", as (host, mount, percent used)."""
    host, mount, percent = line.split()
    return host, mount, float(percent.rstrip("%"))


def level(history):
    """How full a disk is: "ok", "warning" or "critical", from its percent-used readings, oldest first.

    Goes by the lowest of the last three readings, so a single spike never alerts.
    """
    percent = min(history[-3:])
    if percent >= CRITICAL:
        return "critical"
    return "warning" if percent >= WARNING else "ok"


def message(host, mount, history):
    """The line to post in the ops channel about this disk, or None when it is ok."""
    status = level(history)
    if status == "ok":
        return None
    return f"{status.upper()} {host}:{mount} {round(history[-1])}%"


if __name__ == "__main__":
    import sys

    host, mount, percent = parse(sys.argv[1])
    print(message(host, mount, [percent]))
