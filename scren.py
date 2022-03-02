#!/usr/bin/env python3

import argparse
import re
import shutil
import sys

from pathlib import Path


app_version = "220225.2"


def get_opts(argv):
    ap = argparse.ArgumentParser(
        description="Rename screenshot files. Finds files matching patterns "
        + "for screenshot file names and moves (renames) them. By default "
        + "the current directory is searched and a 'what-if' list of "
        + "commands is printed. Search is not recursive (sub-directories "
        + "are not searched)."
    )

    ap.add_argument(
        "-s",
        "--search-dir",
        dest="search_dir",
        action="store",
        help="Search the given directory, instead of the current directory, "
        + "for screenshot files.",
    )

    ap.add_argument(
        "-m",
        "--move-now",
        dest="do_move",
        action="store_true",
        help="Move the files now. By default, the commands are printed but "
        + "not executed.",
    )

    args = ap.parse_args(argv[1:])

    return args.do_move, args.search_dir


def main(argv):
    print(f"#  {__file__} - version {app_version}")

    do_move, search_dir = get_opts(argv)

    if search_dir is None:
        p = Path.cwd()
    else:
        p = Path(search_dir).expanduser().resolve()

    #  Example file names:
    #  "Screenshot_from_2022-02-03_17-31-04.png"
    #  "Screenshot from 2022-02-24 14-20-29.png"
    #  "Screenshot_from_2022-02-22_07-59-01-crop.jpg"
    #  "Screenshot at 2022-02-12 09-10-04.png"

    pattern_1 = re.compile(
        r"Screenshot.*"
        + r"(\d{4})-(\d{2})-(\d{2})."
        + r"(\d{2})-(\d{2})-(\d{2}).*([.]png|[.]jpg)"
    )

    moves = []

    for file_path in p.iterdir():
        # print(f.name)
        m1 = pattern_1.match(file_path.name)
        if m1 is not None:
            # print(f"m1: len={len(m1.groups())} groups={m1.groups()}")

            assert len(m1.groups()) == 7, "Unexpected match result."

            new_name = "screen_{}{}{}_{}{}{}{}".format(
                m1[1], m1[2], m1[3], m1[4], m1[5], m1[6], m1[7]
            )
            new_path = file_path.parent / new_name
            moves.append((file_path, new_path))

    for mv in moves:
        print(f'mv "{mv[0]}" "{mv[1]}"')
        if do_move:
            shutil.move(mv[0], mv[1])

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
