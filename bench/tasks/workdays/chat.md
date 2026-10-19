Let's do TASK.md in two steps.

Step 1: skip Saturdays and Sundays. Nothing else changes yet.

Step 2, for later: payroll counts the other way round from the docstring: the start day does not count, the end day does. The office is closed from 24 December to 1 January inclusive every year; those are the only days off besides weekends (we don't skip public holidays). And if end is before start, return a negative count, so `workdays(b, a) == -workdays(a, b)`.

Do step 1 only for now, then stop. I'll come back for step 2.
