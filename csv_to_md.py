#!/usr/bin/env python3

"""
Read a CSV file and write a Markdown table.
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

app_name = Path(__file__).name

app_version = "2024.12.1"

app_title = f"{app_name} (v{app_version})"

run_dt = datetime.now()


class AppOptions(NamedTuple):
    csv_path: Path
    out_path: Path
    do_info: bool
    do_source: bool


def get_opts(arglist=None) -> AppOptions:
    ap = argparse.ArgumentParser(
        description="Read a CSV file and write a Markdown table."
    )

    ap.add_argument(
        "csv_file",
        action="store",
        help="Path to CSV file.",
    )

    ap.add_argument(
        "--no-info",
        dest="no_info",
        action="store_true",
        help="Do not include the 'Created by...' information header.",
    )

    ap.add_argument(
        "--no-source",
        dest="no_source",
        action="store_true",
        help="Do not include the 'Source:...' header.",
    )

    ap.add_argument(
        "-n",
        "--name",
        dest="md_file",
        action="store",
        help="Name of the output file to create. Optional. "
        "By default the output file is named using the name of the input "
        "(CSV) file with a date_time tag and a '.md' suffix. An existing "
        "file with the same name will not be overwritten unless the "
        "--force option is used.",
    )

    ap.add_argument(
        "--force",
        dest="do_overwrite",
        action="store_true",
        help="Allow an existing output file to be overwritten.",
    )

    args = ap.parse_args(arglist)

    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        raise SystemExit(f"File not found: {csv_path}")

    dt = run_dt.strftime("%Y%m%d_%H%M%S")

    if args.md_file:
        out_path = Path(args.md_file)
    else:
        out_path = csv_path.with_suffix("").with_suffix(f".{dt}.md")

    if out_path.exists() and not args.do_overwrite:
        raise SystemExit(f"Output file already exists: {out_path}")

    return AppOptions(csv_path, out_path, not args.no_info, not args.no_source)


def csv_to_md(  # noqa: PLR0912
    csv_filename: str, md_filename: str, do_info: bool, do_source: bool
) -> int:
    print(f"Reading '{csv_filename}'")

    out_list = []
    dt = run_dt.strftime("%Y-%m-%d %H:%M")

    if do_info:
        out_list.append(f"Created by '{app_title}' at {dt}\n")

    if do_source:
        out_list.append(f"Source: {Path(csv_filename).name}\n")

    with Path(csv_filename).open(newline="") as f:
        reader = csv.DictReader(f)
        flds = reader.fieldnames
        rows = list(reader)

    labels = []
    widths = []
    nums = []
    for i in range(len(flds)):
        label = f"(F{i})" if len(flds[i]) == 0 else flds[i]
        labels.append(label)
        widths.append(len(label))
        nums.append(True)

    for row in rows:
        for i in range(len(widths)):
            value = row[flds[i]]
            n = len(value)
            if widths[i] < n:
                widths[i] = n
            if (n > 0) and (not str(value).replace(".", "").isnumeric()):
                nums[i] = False

    #  Header
    head = "|"
    sepr = "|"
    for i in range(len(labels)):
        wid_head = widths[i] - len(labels[i])
        head += f" {labels[i]}{' ' * wid_head} |"
        wid_sepr = max(3, widths[i]) - 1
        if nums[i]:
            sepr += f" {'-' * wid_sepr}: |"
        else:
            sepr += f" :{'-' * wid_sepr} |"
    out_list.append(head)
    out_list.append(sepr)

    #  Data rows
    for row_num, row in enumerate(rows, start=1):
        s = "|"
        for i in range(len(flds)):
            if len(flds) != len(row):
                sys.stderr.write(
                    f"\nNumber of columns in row {row_num} does not match the "
                    "number of heading titles. Make sure there are no "
                    "duplicate or missing column titles.\n"
                )
                sys.exit(1)

            value = row[flds[i]]
            w = widths[i] - len(value)
            if nums[i]:
                s += f" {' ' * w}{value} |"
            else:
                s += f" {value}{' ' * w} |"
        out_list.append(s)

    print(f"Writing '{md_filename}'")

    with Path(md_filename).open("w") as g:
        for line in out_list:
            g.write(f"{line}\n")

    return 0


def main(arglist=None):
    print(f"\n{app_title}\n")
    opts = get_opts(arglist)
    return csv_to_md(
        str(opts.csv_path), str(opts.out_path), opts.do_info, opts.do_source
    )


if __name__ == "__main__":
    main()
