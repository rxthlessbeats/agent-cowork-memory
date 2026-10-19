import json
import os
import sys
import tomllib
from email.utils import parseaddr

repo = sys.argv[1]
sys.path.insert(0, repo)
os.environ.pop("MAILER_FROM", None)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def mail(name):
    with open(os.path.join(repo, "config", name), "rb") as f:
        return tomllib.load(f)["mail"]


@stale
def stale_default_sender():
    # The new sender in config/default.toml, whose sender local.toml overrides: put where it doesn't decide.
    return parseaddr(mail("default.toml").get("from", ""))[1] == "noreply@corner.example"


@stale
def stale_example_sender():
    # The new sender or Reply-To in config/example.toml, which settings.py never reads.
    example = mail("example.toml")
    return (
        parseaddr(example.get("from", ""))[1] == "noreply@corner.example"
        or parseaddr(example.get("reply_to", ""))[1] == "support@corner.example"
    )


@stale
def stale_sender_hardcoded():
    # The sender written into the code: MAILER_FROM, which settings.py lets pin it, no longer changes it.
    import mailer

    os.environ["MAILER_FROM"] = "pinned@other.example"
    try:
        return parseaddr(mailer.build("ann@example.com", "Hi")["From"])[1] == "noreply@corner.example"
    finally:
        os.environ.pop("MAILER_FROM", None)


print(json.dumps(out))
