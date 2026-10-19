"""Logging for the service, set up once when it starts."""

import logging.config
import os

import settings

CONFIG_DIR = os.path.join(settings.HERE, "logconf")


def setup_logging():
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    path = os.path.join(CONFIG_DIR, f"{settings.APP_ENV}.ini")
    logging.config.fileConfig(path, defaults={"logdir": settings.LOG_DIR}, disable_existing_loggers=False)
