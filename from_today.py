#!/usr/bin/env python3

"""
from_today.py

Prints future dates for a list of days from today.

The initial purpose of this script is to calculate options for the date
to use when labelling a "keep until" folder.
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
