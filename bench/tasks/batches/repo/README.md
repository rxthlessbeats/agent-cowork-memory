# Warehouse sync

`sync.py` moves rows between our database and the warehouse: export sends our rows there, import saves the warehouse's rows here.

## Batches

Export and import both move rows in batches of `settings.BATCH_SIZE` (5,000 rows); the last batch may be smaller. A transfer always ends with an empty batch, which tells the other side it is complete.
