# Prune old archives

The backup folder keeps growing. Add `prune(folder, today)` to archive.py: it deletes the archives in folder that are past their keep period (see README.md) and returns the names of the ones it deletes. `today` is a date.
