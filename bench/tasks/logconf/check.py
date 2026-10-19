import configparser
import io
import json
import logging
import os
import shutil
import sys
import tempfile

# setup_logging writes log files: the checks run on a copy of the folder, so they leave nothing behind in it.
tmp = tempfile.mkdtemp()
repo = os.path.join(tmp, "repo")
shutil.copytree(sys.argv[1], repo, symlinks=True, ignore=shutil.ignore_patterns(".git"))
os.chdir(repo)
sys.path.insert(0, repo)
# The live config is the one setup_logging picks when nothing is set.
for name in ("APP_ENV", "LOG_DIR"):
    os.environ.pop(name, None)
# A handler on stdout mustn't spoil the JSON below.
stdout, sys.stdout = sys.stdout, io.StringIO()
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@check
def step1_redact():
    import db

    return (
        db.redact("postgres://shop:secret@db:5432/shop") == "postgres://shop:***@db:5432/shop"
        and db.redact("postgres://app:pa55@localhost/orders") == "postgres://app:***@localhost/orders"
        and db.redact("postgres://reader@db:5432/shop") == "postgres://reader@db:5432/shop"
    )


@check
def goal_db_log():
    import logsetup

    logsetup.setup_logging()
    logger = logging.getLogger("db")
    path = os.path.join(repo, "logs", "db.log")
    start = os.path.getsize(path) if os.path.exists(path) else 0
    logger.info("check: an info line")
    logger.warning("check: a warning line")
    with open(path, "rb") as f:
        f.seek(start)
        written = f.read().decode("utf-8")
    return (
        logger.getEffectiveLevel() == logging.WARNING
        and "check: a warning line" in written
        and "check: an info line" not in written
    )


@check
def found_prod_ini():
    # settings.py's APP_ENV defaults to "prod", so setup_logging loads logconf/prod.ini, not the fuller dev.ini.
    ini = configparser.ConfigParser(interpolation=None)
    ini.read(os.path.join(repo, "logconf", "prod.ini"), encoding="utf-8")
    loggers = [ini[f"logger_{name.strip()}"] for name in ini["loggers"]["keys"].split(",")]
    [db] = [section for section in loggers if section.get("qualname") == "db"]
    handlers = [ini[f"handler_{name.strip()}"] for name in db.get("handlers", "").split(",") if name.strip()]
    files = [handler.get("args", "") + handler.get("kwargs", "") for handler in handlers]
    return db.get("level", "").upper() in ("WARNING", "WARN") and any("db.log" in f for f in files)


logging.shutdown()
sys.stdout = stdout
shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(out))
