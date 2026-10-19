"""The shop service: python app.py"""

import logging

import db
from logsetup import setup_logging

log = logging.getLogger("app")


def main():
    setup_logging()
    log.info("starting")
    db.connect()
    log.info("ready")


if __name__ == "__main__":
    main()
