# Cinema tickets

The box office still works prices out by hand. Add `quote(show, kinds, now)` to tickets.py: what one ticket of each kind in `kinds` ("adult", "student" or "senior") costs together for `show` (a dict as in shows.py), in cents, bought online at `now` (a datetime); or None once online sales for the show have closed. Seniors get the usual senior discount.
