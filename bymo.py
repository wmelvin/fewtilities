#!/usr/bin/env python3

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

app_version = "2024.01.1"

app_title = f"bymo.py (v{app_version})"


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


def get_opts(argv):
    ap = argparse.ArgumentParser(
        description="Move files in the current directory (folder) to "
        "sub-directories named for the year and month the file was "
        "last modified."
    )

    ap.add_argument(
        "filespecs",
        nargs="*",
        action="store",
        help="Optional file specification for matching files to move (ie. '*.jpg').",
    )

    ap.add_argument(
        "-m",
        "--move-now",
        dest="do_move",
        action="store_true",
        help="Move the files now. By default, the commands are printed but "
        "not executed.",
    )

    ap.add_argument(
        "-k",
        "--keep-spaces",
        dest="keep_spaces",
        action="store_true",
        help="Keep spaces in destination file names. By default, spaces are "
        "replaced with underscores.",
    )

    ap.add_argument(
        "--what-if",
        dest="what_if",
        action="store_true",
        help="Print the list of files that would be moved.",
    )

    args = ap.parse_args(argv[1:])

    return args.do_move, args.keep_spaces, args.filespecs, args.what_if


def main(argv):  # noqa: PLR0912
    print(f"#  {app_title}")

    do_move, keep_spaces, filespecs, what_if = get_opts(argv)

    p = Path.cwd()

    if len(filespecs) == 0:
        files = [x for x in p.iterdir() if x.is_file() and x.name != __file__]
    else:
        files = []
        for spec in filespecs:
            files += sorted(p.glob(spec))

    dirs = []
    moves = []

    for f in files:
        dst_dir = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y_%m")

        if dst_dir not in dirs:
            dirs.append(dst_dir)

        dst_name = f.name if keep_spaces else f.name.replace(" ", "_")

        moves.append((f.name, Path(dst_dir) / dst_name, dst_dir))

    dirs.sort()

    if what_if:
        print("\n#  Printing Unix 'mv' commands for '--what-if' output.\n")
        for d in dirs:
            print(f'mkdir "{d}"')

    for mv in moves:
        if what_if:
            print(f'mv "{mv[0]}" "{mv[1]}"')
            continue

        print(f'Move "{mv[0]}"')
        print(f'  to "{mv[1]}"')

        dst_path = Path(mv[2])

        if do_move:
            if not dst_path.exists():
                dst_path.mkdir()
            shutil.move(mv[0], mv[1])
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
                if not dst_path.exists():
                    dst_path.mkdir()
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
