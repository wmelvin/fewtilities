#!/usr/bin/env python3

import argparse
import re
import shutil
import sys

from pathlib import Path


app_version = "230116.1"

app_title = f"scren.py (v.{app_version})"


def get_input_lower(prompt):
    return input(prompt).lower()


def get_user_input(prompt, choices, default=None):
    assert 0 < len(choices)
    assert all([x == x.lower() for x in choices])
    while True:
        answer = get_input_lower(prompt)
        if answer == "":
            if default is not None:
                answer = default
                break
        else:
            if answer in choices:
                break
        print("Please select from the list of valid choices.")
    return answer


def get_opts(argv):
    ap = argparse.ArgumentParser(
        description="Rename screenshot files. Finds files matching patterns "
        + "for screenshot file names and moves (renames) them. By default "
        + "the current directory is searched and a prompt is displayed "
        + "asking whether the file should be moved. The default answer is "
        + "Yes (Y) if Enter is pressed without any other input. The prompt "
        + "also includes the option to move all files (A), or to quit (Q). "
        + "Search is not recursive (sub-directories are not searched)."
    )

    ap.add_argument(
        "-s",
        "--search-dir",
        dest="search_dir",
        action="store",
        help="Search the given directory, instead of the current directory, "
        + "for screenshot files. Search is not recursive (sub-directories "
        + "are not searched).",
    )

    ap.add_argument(
        "-m",
        "--move-now",
        dest="do_move",
        action="store_true",
        help="Move the files now instead of prompting whether to "
        + "move each file.",
    )

    ap.add_argument(
        "--what-if",
        dest="what_if",
        action="store_true",
        help="Print the list of files that would be moved.",
    )

    args = ap.parse_args(argv[1:])

    return args.do_move, args.search_dir, args.what_if


def main(argv):
    print(f"#  {app_title}")

    do_move, search_dir, what_if = get_opts(argv)

    if search_dir is None:
        p = Path.cwd()
    else:
        p = Path(search_dir).expanduser().resolve()

    #  Example pattern_1 file names:
    #  "Screenshot_from_2022-02-03_17-31-04.png"
    #  "Screenshot from 2022-02-24 14-20-29.png"
    #  "Screenshot_from_2022-02-22_07-59-01-crop.jpg"
    #  "Screenshot at 2022-02-12 09-10-04.png"

    pattern_1 = re.compile(
        r"Screenshot.*"
        + r"(\d{4})-(\d{2})-(\d{2})."
        + r"(\d{2})-(\d{2})-(\d{2}).*([.]png|[.]jpg)"
    )

    #  Example pattern_2 file names:
    #  "Screenshot_20220301_070842.png"

    pattern_2 = re.compile(
        r"Screenshot.*"
        + r"(\d{8})."
        + r"(\d{6}).*([.]png|[.]jpg)"
    )

    moves = []

    for file_path in p.iterdir():
        # print(f.name)
        m1 = pattern_1.match(file_path.name)
        if m1 is None:
            m2 = pattern_2.match(file_path.name)
            if m2 is not None:
                assert len(m2.groups()) == 3, "Unexpected match result."
                new_name = "screen_{}_{}{}".format(
                    m2[1], m2[2], m2[3]
                )
                new_path = file_path.parent / new_name
                moves.append((file_path, new_path))

        else:
            # print(f"m1: len={len(m1.groups())} groups={m1.groups()}")
            assert len(m1.groups()) == 7, "Unexpected match result."
            new_name = "screen_{}{}{}_{}{}{}{}".format(
                m1[1], m1[2], m1[3], m1[4], m1[5], m1[6], m1[7]
            )
            new_path = file_path.parent / new_name
            moves.append((file_path, new_path))

    if what_if:
        print("\n#  Printing Unix 'mv' commands for '--what-if' output.\n")

    for mv in moves:
        if what_if:
            print(f'mv "{mv[0]}" "{mv[1]}"')
            continue

        print(f'Move "{mv[0]}"')
        print(f'  to "{mv[1]}"')

        if do_move:
            shutil.move(mv[0], mv[1])
            print("(moved)")
        else:
            ans = get_user_input(
                "Move (rename) file?  Enter (Y)es, (n)o, (a)ll, or (q)uit: ",
                "y,n,a,q",
                "y"
            )

            if ans == "n":
                print("(Not moved)")
                continue

            if ans == "y" or ans == "a":
                shutil.move(mv[0], mv[1])
                print("(Moved)")

            if ans == "a":
                do_move = True

            if ans == "q":
                print("(Quit)")
                break

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
