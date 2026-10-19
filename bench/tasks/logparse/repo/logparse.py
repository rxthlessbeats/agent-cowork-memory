"""Parse our app's log lines into records.

A line looks like this:

    2024-05-01 12:00:03 WARN [billing] card declined user=42
"""


def parse_line(line):
    """Return a record dict for one log line."""
    raise NotImplementedError


def parse(text):
    """Records for every log line in text."""
    return [parse_line(line) for line in text.splitlines() if line.strip()]
