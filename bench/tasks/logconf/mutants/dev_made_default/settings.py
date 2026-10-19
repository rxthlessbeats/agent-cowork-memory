"""Service settings, from the environment."""

import os

HERE = os.path.dirname(os.path.abspath(__file__))

APP_ENV = os.environ.get("APP_ENV", "dev")
LOG_DIR = os.environ.get("LOG_DIR", os.path.join(HERE, "logs"))
DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://shop:shop@localhost:5432/shop")
