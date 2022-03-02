#!/usr/bin/env python3

import argparse
import shutil
import sys

from datetime import datetime
from pathlib import Path


app_version = "220302.1"


def get_opts(argv):
    ap = argparse.ArgumentParser(
        description="Move files in the current directory (folder) to "
        + "sub-directories named for the year and month the file was "
        + "last modified."
    )

    ap.add_argument(
        "filespecs",
        nargs="*",
        action="store",
        help="Optional file specification for matching files to move "
        + "(ie. '*.jpg').",
    )

    ap.add_argument(
        "-m",
        "--move-now",
        dest="do_move",
        action="store_true",
        help="Move the files now. By default, the commands are printed but "
        + "not executed.",
    )

    ap.add_argument(
        "-k",
        "--keep-spaces",
        dest="keep_spaces",
        action="store_true",
        help="Keep spaces in destination file names. By default, spaces are "
        + "replaced with underscores.",
    )

    args = ap.parse_args(argv[1:])

    return args.do_move, args.keep_spaces, args.filespecs


def main(argv):
    print(f"#  {__file__} - version {app_version}")

    do_move, keep_spaces, filespecs = get_opts(argv)

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

        if keep_spaces:
            dst_name = f.name
        else:
            dst_name = f.name.replace(" ", "_")

        moves.append((f.name, Path(dst_dir) / dst_name))

    dirs.sort()

    for d in dirs:
        print(f"mkdir {d}")
        if do_move:
            dp = Path(d)
            if not dp.exists():
                dp.mkdir()

    for mv in moves:
        print(f'mv "{mv[0]}" "{mv[1]}"')
        if do_move:
            shutil.move(mv[0], mv[1])

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
