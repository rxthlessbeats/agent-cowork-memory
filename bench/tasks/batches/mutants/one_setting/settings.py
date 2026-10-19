"""Settings for the warehouse sync."""

WAREHOUSE_URL = "https://warehouse.example/api/rows"

# Rows per batch, for export and import alike: 2,750 suits both the warehouse and our database's locks.
BATCH_SIZE = 2750
