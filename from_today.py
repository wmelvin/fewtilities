#!/usr/bin/env python3

"""
from_today.py

Print the date for a list of number of days from today.

Initial purpose is to calculate a list of options for the date to use
when putting items into a "keep until" folder.
"""

from datetime import date
from datetime import timedelta


def print_date(days):
    d = date.today() + timedelta(days=days)
    m = round(days / 30.4)
    print(f"{days:3d} days ({m} mo): {d.strftime('%Y-%m-%d')}")


print(f"\n   Today: {date.today()}\n")

for days in [30, 60, 90, 120, 180, 270]:
    print_date(days)
