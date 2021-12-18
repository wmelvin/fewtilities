"""
Read a CSV file and write a Markdown table.
"""

import argparse
import csv
import sys

from collections import namedtuple
from datetime import datetime
from pathlib import Path


AppOptions = namedtuple("AppOptions", "csv_path, out_path")


def get_opts(argv) -> AppOptions:

    ap = argparse.ArgumentParser(
        description="Read a CSV file and write a Markdown table."
    )

    ap.add_argument(
        "csv_file",
        action="store",
        help="Path to CSV file.",
    )

    args = ap.parse_args(argv[1:])

    csv_path = Path(args.csv_file)
    assert csv_path.exists()

    dt = datetime.now().strftime("%Y%m%d_%H%M%S")

    out_path = csv_path.with_suffix("").with_suffix(f".{dt}.md")

    opts = AppOptions(csv_path, out_path)

    return opts


def main(argv):
    opts = get_opts(argv)

    with open(opts.csv_path, newline="") as f:
        reader = csv.DictReader(f)
        flds = reader.fieldnames
        print(flds)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
