#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

app_version = "2024.02.2"

app_title = f"scren.py (v{app_version})"

#  Example pattern_1 file names:
#    "Screenshot_from_2022-02-03_17-31-04.png"
#    "Screenshot from 2022-02-24 14-20-29.png"
#    "Screenshot_from_2022-02-22_07-59-01-crop.jpg"
#    "Screenshot at 2022-02-12 09-10-04.png"

pattern_1 = re.compile(
    r"Screenshot.*"
    r"(\d{4})-(\d{2})-(\d{2})."
    r"(\d{2})-(\d{2})-(\d{2}).*([.]png|[.]jpg)"
)

#  Example pattern_2 file names:
#    "Screenshot_20220301_070842.png"

pattern_2 = re.compile(r"Screenshot.*(\d{8}).(\d{6}).*([.]png|[.]jpg)")


def get_input_lower(prompt):
    return input(prompt).lower()


def get_user_input(prompt, choices, default=None):
    assert len(choices) > 0  # noqa: S101
    assert all(x == x.lower() for x in choices)  # noqa: S101
    while True:
        answer = get_input_lower(prompt)
        if answer == "":
            if default is not None:
                answer = default
                break
        elif answer in choices:
            break
        print("Please select from the list of valid choices.")
    return answer


def get_opts(arglist=None):
    ap = argparse.ArgumentParser(
        description="Rename screenshot files. Finds files matching patterns "
        "for screenshot file names and moves (renames) them. By default "
        "the current directory is searched and a prompt is displayed "
        "asking whether the file should be moved. The default answer is "
        "Yes (Y) if Enter is pressed without any other input. The prompt "
        "also includes the option to move all files (A), or to quit (Q). "
        "Search is not recursive (sub-directories are not searched)."
    )

    ap.add_argument(
        "-s",
        "--search-dir",
        dest="search_dir",
        action="store",
        help="Search the given directory, instead of the current directory, "
        "for screenshot files. Search is not recursive (sub-directories "
        "are not searched).",
    )

    ap.add_argument(
        "-m",
        "--move-now",
        dest="do_move",
        action="store_true",
        help="Move the files now instead of prompting whether to move each file.",
    )

    ap.add_argument(
        "--by-mo",
        dest="by_mo",
        action="store_true",
        help="Move files to monthly sub-directories based on the year and month.",
    )

    ap.add_argument(
        "--what-if",
        dest="what_if",
        action="store_true",
        help="Print the list of files that would be moved.",
    )

    args = ap.parse_args(arglist)

    return args.do_move, args.search_dir, args.by_mo, args.what_if


def get_moves(search_path: Path, by_mo: bool) -> list[tuple[Path, Path]]:
    moves = []
    for file_path in search_path.iterdir():
        m1 = pattern_1.match(file_path.name)
        if m1 is None:
            m2 = pattern_2.match(file_path.name)
            if m2 is not None:
                if len(m2.groups()) != 3:  # noqa: PLR2004
                    print(f"Unexpected match result for {file_path.name}.")
                    continue

                ymd = m2[1]
                hms = m2[2]
                ext = m2[3]
                new_name = f"screen_{ymd}_{hms}{ext}"
                if by_mo:
                    mo_dir = f"{ymd[:4]}_{ymd[4:6]}"
                    new_path = file_path.parent / mo_dir
                    new_path /= new_name
                else:
                    new_path = file_path.parent / new_name
                moves.append((file_path, new_path))

        else:
            if len(m1.groups()) != 7:  # noqa: PLR2004
                print(f"Unexpected match result for {file_path.name}.")
                continue

            ymd = m1[1] + m1[2] + m1[3]
            hms = m1[4] + m1[5] + m1[6]
            ext = m1[7]
            new_name = f"screen_{ymd}_{hms}{ext}"
            if by_mo:
                mo_dir = f"{ymd[:4]}_{ymd[4:6]}"
                new_path = file_path.parent / mo_dir
                new_path /= new_name
            else:
                new_path = file_path.parent / new_name
            moves.append((file_path, new_path))
    return moves


def main(arglist=None):
    print(f"#  {app_title}")

    do_move, search_dir, by_mo, what_if = get_opts(arglist)

    p = Path.cwd() if search_dir is None else Path(search_dir).expanduser().resolve()

    moves = get_moves(p, by_mo)

    if what_if:
        print("\n#  Printing Unix 'mv' commands for '--what-if' output.\n")

    for src, dst in moves:
        if what_if:
            print(f'mv "{src}" "{dst}"')
            continue

        print(f'Move "{src}"')
        print(f'  to "{dst}"')

        if do_move:
            if by_mo and not dst.parent.exists():
                dst.parent.mkdir()
            shutil.move(src, dst)
            print("(moved)")
        else:
            ans = get_user_input(
                "Move (rename) file?  Enter (Y)es, (n)o, (a)ll, or (q)uit: ",
                "y,n,a,q",
                "y",
            )

            if ans == "n":
                print("(Not moved)")
                continue

            if ans in ("y", "a"):
                if by_mo and not dst.parent.exists():
                    dst.parent.mkdir()
                shutil.move(src, dst)
                print("(Moved)")

            if ans == "a":
                do_move = True

            if ans == "q":
                print("(Quit)")
                break

    return 0


if __name__ == "__main__":
    main()
