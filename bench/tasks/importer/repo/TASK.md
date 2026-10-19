# Product importer

Step 1: `shipping_band(weight_kg)` in shipping.py: "S" up to 2 kg, "M" over 2 kg and up to 10 kg, "L" over 10 kg.

Step 2: fix the product data. X-17, the hedge shears, weighs 2.5 kg, not 25 kg. And there's a new product: X-99, "Pruning saw", 0.8 kg. Product lookups (lookup.py) must give both.
