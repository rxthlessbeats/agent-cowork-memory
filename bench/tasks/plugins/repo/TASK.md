# Order export

Step 1: `filename(fmt, day)` in naming.py, giving an export's file name: "csv" on 2026-03-04 gives "orders-2026-03-04.csv".

Step 2: the CSV export uses ";" as its delimiter and starts with a header row of the column names, `id;customer;total`.
