# Backups

Every night the backup job writes one archive per database into the backup folder (`BACKUP_DIR` in settings.py), named after the database and the day, like `orders-2025-03-01.tar.gz`.

Archives are kept for 30 days (`KEEP_DAYS` in settings.py). Anything older is deleted.
