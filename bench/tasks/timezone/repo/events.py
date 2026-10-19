"""Riverside Hall's events, from events.csv: one per line, start,title."""

import csv

from times import parse_time


def load(path):
    with open(path, newline="") as f:
        return [{"start": parse_time(start), "title": title} for start, title in csv.reader(f)]


def upcoming(events, now):
    return sorted((e for e in events if e["start"] >= now), key=lambda e: e["start"])
