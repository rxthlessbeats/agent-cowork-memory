"""Settings for the nightly backup job."""

BACKUP_DIR = "/var/backups/db"
DATABASES = ["orders", "customers", "stock"]

# Days an archive is kept before it is deleted.
KEEP_DAYS = 30
