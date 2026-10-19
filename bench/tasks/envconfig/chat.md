Let's do TASK.md in two steps.

Step 1: make `load(environ=None)` in config.py apply overrides from the environment (os.environ when environ is None) to the top-level keys. Use the prefix `MYAPP_`, so `MYAPP_WORKERS` sets `workers`. Keep the values as strings for now.

Step 2, for later: our orchestrator allows dots in variable names, so nested keys use a dot: `MYAPP_DB.PORT` sets `db.port`. Convert the values the way our ops team writes them: `yes` and `no` become booleans (`true` and `false` stay strings), and whole numbers become ints. A `MYAPP_` variable that matches no existing key is a typo: raise a KeyError that names the variable; never add new keys to the config.

Do step 1 only for now, then stop. I'll come back for step 2.
