"""Settings for the warehouse sync."""

WAREHOUSE_URL = "https://warehouse.example/api/rows"

# Different on purpose: the warehouse takes up to 7,500 rows a request, and imports over 2,750 hold our locks too long.
EXPORT_BATCH_SIZE = 7500
IMPORT_BATCH_SIZE = 2750
