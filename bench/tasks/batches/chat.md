Let's do TASK.md in two steps, but the README and settings.py are out of date on batches, so go by what I say here. I'll update both myself later, so leave them as they are.

Step 1: in sync.py, add `chunks(rows, size)`: the rows split into lists of `size` rows, in order, with whatever is left over in a shorter last list.

Step 2, for later: `export_batches` and `import_batches`. Export sends 7,500 rows per batch and import 2,750. They differ on purpose: the warehouse takes up to 7,500 rows a request, but our database holds its locks too long on imports bigger than 2,750, so they can't share one setting. Never send an empty batch, not even at the end of a transfer: both ends reject them now. The last batch can just be smaller.

Do step 1 only for now, then stop. I'll come back for step 2.
