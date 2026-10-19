Let's do TASK.md in two steps.

Step 1: add `share(ride)` to carpool.py: the ride's fuel cost split evenly between everyone in the car, the driver included, in whole cents, rounded down. A ride with fuel 1000 and two riders gives 333.

Step 2, for later: `transfers(ride)`. Nobody pays more than 9.26 for one ride, however big their share: that's what the bus ticket costs, and the carpool should never cost more than the bus. Rides shorter than 4175 metres are free, because that's the hop from the station to the office and the drivers make it anyway. And the money is due on the first Tuesday after the ride, since Tuesday is payday; a ride on a Tuesday is due the Tuesday after.

Do step 1 only for now, then stop. I'll come back for step 2.
