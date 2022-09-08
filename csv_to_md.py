#!/usr/bin/env python3

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
    assert csv_path.exists(), "Specified CSV file does not exist."

    dt = datetime.now().strftime("%Y%m%d_%H%M%S")

    out_path = csv_path.with_suffix("").with_suffix(f".{dt}.md")

    opts = AppOptions(csv_path, out_path)

    return opts


def csv_to_md(csv_filename: str, md_filename: str) -> int:
    print(f"Reading '{csv_filename}'")

    out_list = []
    out_list.append(f"{Path(csv_filename).name}")
    out_list.append("")

    with open(csv_filename, newline="") as f:
        reader = csv.DictReader(f)
        flds = reader.fieldnames
        # print(flds)
        rows = [row for row in reader]

    labels = []
    widths = []
    nums = []
    for i in range(len(flds)):
        if len(flds[i]) == 0:
            label = f"(F{i})"
        else:
            label = flds[i]
        labels.append(label)
        widths.append(len(label))
        nums.append(True)

    for row in rows:
        for i in range(len(widths)):
            value = row[flds[i]]
            n = len(value)
            if widths[i] < n:
                widths[i] = n
            if (0 < n) and (not str(value).replace(".", "").isnumeric()):
                nums[i] = False

    #  Header
    head = "|"
    sepr = "|"
    for i in range(len(labels)):
        wid_head = widths[i] - len(labels[i])
        head += f" {labels[i]}{' ' * wid_head} |"
        wid_sepr = max(3,  widths[i]) - 1
        if nums[i]:
            sepr += f" {'-' * wid_sepr}: |"
        else:
            sepr += f" :{'-' * wid_sepr} |"
    out_list.append(head)
    out_list.append(sepr)

    #  Data rows
    for row in rows:
        s = "|"
        for i in range(len(flds)):

            #  If this assertion fails, check that the headings in the CSV
            #  file are unique.
            assert len(flds) == len(row), "CSV column titles must be unique."

            value = row[flds[i]]
            w = widths[i] - len(value)
            if nums[i]:
                s += f" {' ' * w}{value} |"
            else:
                s += f" {value}{' ' * w} |"
        out_list.append(s)

    # for line in out_list:
    #     print(line)

    print(f"Writing '{md_filename}'")

    with open(md_filename, "w") as g:
        for line in out_list:
            g.write(f"{line}\n")

    return 0


def main(argv):
    opts = get_opts(argv)
    return csv_to_md(str(opts.csv_path), str(opts.out_path))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
