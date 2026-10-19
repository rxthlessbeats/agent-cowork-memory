import json
import os
import sys
import tomllib
from email.utils import parseaddr

repo = sys.argv[1]
sys.path.insert(0, repo)
# settings.py lets MAILER_FROM override every file: the checks look at the files alone.
os.environ.pop("MAILER_FROM", None)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@check
def step1_domain():
    import addresses

    return addresses.domain("Ann@Corner.Example") == "corner.example" and addresses.domain("bo@mail.shop.org") == "mail.shop.org"


@check
def goal_sender():
    import mailer

    headers = mailer.build("ann@example.com", "Your order")
    return (
        parseaddr(headers["From"])[1] == "noreply@corner.example"
        and parseaddr(headers["Reply-To"])[1] == "support@corner.example"
        and headers["To"] == "ann@example.com"
        and headers["Subject"] == "Your order"
    )


@check
def found_local_toml():
    # settings.py reads config/local.toml after config/default.toml, and local.toml sets a sender of its own: the new
    # one belongs there.
    with open(os.path.join(repo, "config", "local.toml"), "rb") as f:
        mail = tomllib.load(f)["mail"]
    return parseaddr(mail["from"])[1] == "noreply@corner.example"


print(json.dumps(out))
