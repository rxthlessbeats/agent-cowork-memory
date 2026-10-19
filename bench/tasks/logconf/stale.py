import configparser
import io
import json
import logging
import logging.config
import os
import shutil
import sys
import tempfile

# setup_logging writes log files: like check.py, this runs on a copy of the folder, so it leaves nothing behind in it.
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


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def step2(name):
    """Whether logconf/<name> has step 2: the db logger at WARNING, with a handler writing db.log."""
    ini = configparser.ConfigParser(interpolation=None)
    ini.read(os.path.join(repo, "logconf", name), encoding="utf-8")
    loggers = [ini[f"logger_{key.strip()}"] for key in ini["loggers"]["keys"].split(",")]
    for db in (section for section in loggers if section.get("qualname") == "db"):
        handlers = [ini[f"handler_{key.strip()}"] for key in db.get("handlers", "").split(",") if key.strip()]
        files = [handler.get("args", "") + handler.get("kwargs", "") for handler in handlers]
        return db.get("level", "").upper() in ("WARNING", "WARN") and any("db.log" in f for f in files)
    return False


def setup_without_ini():
    """Runs setup_logging with logging.config.fileConfig stubbed out. Returns the ini files it asked for."""
    import logsetup

    asked = []
    real = logging.config.fileConfig
    logging.config.fileConfig = lambda fname, *args, **kwargs: asked.append(os.path.basename(str(fname)))
    try:
        logsetup.setup_logging()
    finally:
        logging.config.fileConfig = real
    return asked


@stale
def stale_dev_db_log():
    # Step 2 in logconf/dev.ini, which only APP_ENV=dev loads, and not in prod.ini, the one the service starts with.
    # (dev.ini having it as well as prod.ini is a choice, not a mistake.)
    return step2("dev.ini") and not step2("prod.ini")


@stale
def stale_dev_ini_live():
    # With nothing set, setup_logging loads an ini other than logconf/prod.ini: another one was made the live one.
    asked = setup_without_ini()
    return bool(asked) and asked != ["prod.ini"]


@stale
def stale_db_log_in_code():
    # The db logger set up in code: with no ini loaded at all, setup_logging still makes it WARNING or gives it a
    # db.log handler.
    setup_without_ini()
    db = logging.getLogger("db")
    return db.level == logging.WARNING or any("db.log" in str(getattr(h, "baseFilename", "")) for h in db.handlers)


logging.shutdown()
sys.stdout = stdout
shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(out))
