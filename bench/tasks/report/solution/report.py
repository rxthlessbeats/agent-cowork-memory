import argparse
import csv
import sys


def load(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def totals(rows):
    out = {}
    for row in rows:
        out[row["category"]] = out.get(row["category"], 0) + int(row["amount_cents"])
    return out


def main(argv):
    parser = argparse.ArgumentParser(prog="report.py")
    parser.add_argument("command", choices=["summary"])
    parser.add_argument("file", nargs="?", default="sales.csv")
    parser.add_argument("--top", type=int)
    args = parser.parse_args(argv)
    ranked = sorted(totals(load(args.file)).items(), key=lambda kv: -kv[1])
    for category, cents in ranked[: args.top]:
        print(f"{category}: ${cents / 100:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
