Let's do TASK.md in two steps.

Step 1: add `parse_items(text)` to bakery.py. It reads an order the way people write it: `parse_items("2 sourdough, 1 cinnamon bun")` is `{"sourdough": 2, "cinnamon bun": 1}`, and an item named twice adds up, so `parse_items("1 rye, 2 rye")` is `{"rye": 3}`.

Step 2, for later: `accept` and `total`. An order needs at least 81 minutes between when it's placed and the pickup, because that's how long our last bake takes from the oven to the shelf. And no pickups on a Friday: that's market day, and the oven is full with the market stall's bread. Placing an order on a Friday for another day is fine.

Do step 1 only for now, then stop. I'll come back for step 2.
