# Payroll

`payroll.pay(hours, rate)` works out a week's gross pay from the hours worked that week and the hourly rate.

Step 1: `parse_hours(text)` in payroll/timesheet.py, turning a timesheet entry in hours and minutes, like "7:45", into the float 7.75.

Step 2: overtime from 38 hours. The new agreement moves the overtime threshold from 40 hours a week to 38: every hour over 38 in a week is paid at 1.5 times the hourly rate. `payroll.pay` must pay it that way.
