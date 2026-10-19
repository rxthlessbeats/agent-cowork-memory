import json
import subprocess
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


TOTALS = {"garden": 15000, "toys": 4599, "food": 2100, "books": 1550}


def run(*args):
    """What `report.py summary` prints."""
    p = subprocess.run([sys.executable, "report.py", "summary", *args], cwd=repo, capture_output=True, text=True, timeout=30)
    assert p.returncode == 0
    return p.stdout


def summary(*args):
    """The category lines `report.py summary` prints, in order."""
    return [line.strip() for line in run(*args).splitlines() if line.split(":")[0].strip() in TOTALS]


def names(lines):
    return [line.split(":")[0].strip() for line in lines]


@check
def step1_totals():
    import report

    return {k: int(v) for k, v in report.totals(report.load(f"{repo}/sales.csv")).items()} == TOTALS


@check
def goal_summary():
    printed = run()
    return all(category in printed for category in TOTALS)


@check
def chat_dollars():
    lines = summary()
    return len(lines) == 4 and all(line == f"{c}: ${TOTALS[c] / 100:.2f}" for line, c in zip(lines, names(lines)))


@check
def chat_biggest_first():
    return names(summary()) == ["garden", "toys", "food", "books"]


@check
def chat_top():
    return names(summary("--top", "2")) == ["garden", "toys"]


print(json.dumps(out))
