# Ferry tickets

The booking site has to print tickets. Add `ticket(booking)` to tickets.py. A booking is a dict with `departure` (the sailing's time, "HH:MM"), `adults` (how many passengers) and `vehicle` (its length in mm, or None for foot passengers). It returns a dict with `price` (cents), `lane` ("car" or "long" for a booking with a vehicle, None without one), `check_in` (when check-in closes, "HH:MM") and `boarding` (when boarding starts, "HH:MM").
