#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

app_version = "2024.02.1"

app_title = f"copydif.py (v{app_version})"

log_file = None


def write_log(text: str):
    if log_file:
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with Path(log_file).open("a") as f:
            f.write(f"[{dt}] {text.strip()}\n")


def say(text: str):
    """
    Prints the text string, then passes it to write_log.
    """
    print(text)
    write_log(text)


def complain(text: str):
    """
    Like 'say', but prints the text string to stderr before passing
    it to write_log.
    """
    sys.stderr.write(f"{text}\n")
    write_log(text)


def file_time_str(secs):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(secs))


def same_time_and_size(file1: Path, file2: Path):
    """
    Compares the file size and modified time. Returns False if either
    does not match. Also returns False if file2 does not exist.

    Since the file modification times may have different numeric precision
    on different operating systems, strings representing the times are
    compared instead of comparing the floating point (st_mtime) values.
    """
    if not file2.exists():
        return False

    info1 = file1.stat()
    info2 = file2.stat()
    if info1.st_size != info2.st_size:
        return False

    if file_time_str(info1.st_mtime) != file_time_str(info2.st_mtime):
        return False
    return True


def copy_differing_files(source_spec, target_dir):
    say(f"Source: {source_spec}")
    say(f"Target: {target_dir}")

    source_path = Path(source_spec)

    if source_path.is_dir():
        source_files = [p for p in source_path.iterdir() if p.is_file()]
    else:
        source_files = [
            p for p in source_path.parent.glob(source_path.name) if p.is_file()
        ]

    if not source_files:
        say(f"No files found matching '{source_spec}'")
        return

    source_files.sort()

    for source_file in source_files:
        target_file = Path(target_dir) / source_file.name

        if same_time_and_size(source_file, target_file):
            say(f"  Same: {source_file.name}")
        else:
            say(f"  COPY: {source_file.name}")
            #  shutil.copy2 preserves the file modification time.
            shutil.copy2(source_file, target_file)


def get_source_list(source_spec: str) -> list[str]:
    assert source_spec.startswith("@")  # noqa: S101
    file_name = source_spec.strip("@")
    say(f"Reading list-file: {file_name}")
    if not Path(file_name).exists():
        complain(f"Cannot find source list file: '{file_name}'")
        raise SystemExit
    result = []
    with Path(file_name).open() as f:
        lines = f.readlines()
    for line in lines:
        s = line.strip()
        #  List-file can have comments.
        if s and not s.startswith("#"):
            result.append(s)
    return result


def get_args(arglist=None):
    ap = argparse.ArgumentParser(
        description=(
            "Copy only files that have different sizes or modification "
            "times, or are not present in the target directory. This will "
            "overwrite a newer file in the target directory with an older "
            "file from the source directory (rollback)."
        )
    )

    ap.add_argument(
        "source_spec",
        type=str,
        action="store",
        help="Source directory or file specification. This can be the path "
        "for a single file. It can also include a wilcard character to "
        "match multiple files ('source/path/*.txt' for example). If a "
        "directory name is given then all files in the directory are "
        "included, but sub-directories are not. This script does not do "
        "recursive processing of sub-directories. The source can also be "
        "a list file (a text file with the path to a source file on each "
        "line) if the file name is prefixed with an '@' symbol.",
    )

    ap.add_argument(
        "target_dir",
        type=str,
        action="store",
        help="Directory to update with any changed files.",
    )

    ap.add_argument(
        "--log-file",
        dest="log_file",
        type=str,
        action="store",
        help="Name of the log file to create (or append, if exists). By "
        "default, there is no log file.",
    )

    args = ap.parse_args(arglist)

    if args.log_file:
        log_path = Path(args.log_file)
        if log_path.exists() and not log_path.is_file():
            sys.stderr.write(
                "\nERROR: The specified log file exists but is not a file. "
                "Make sure to provide the full name of the log file, not "
                "just the directory name."
            )
            sys.stderr.write(f"Not a file: {log_path}\n")
            raise SystemExit
    else:
        log_path = None

    if log_path:
        global log_file  # noqa: PLW0603
        log_file = str(log_path)

    source_spec = args.source_spec

    if str(source_spec).startswith("@"):
        source_list = get_source_list(source_spec)
    else:
        source_list = None

    target_dir = args.target_dir
    p = Path(target_dir)
    if not p.exists():
        complain(f"Cannot find target '{p}'")
        raise SystemExit
    if not p.is_dir():
        complain(f"Target must be a directory: '{p}'")
        raise SystemExit

    return (source_spec, target_dir, source_list)


def main(arglist=None):
    print(f"\n{app_title}\n")

    source_spec, target_dir, source_list = get_args(arglist)

    write_log(app_title)

    if source_list is None:
        copy_differing_files(source_spec, target_dir)
    else:
        for item in source_list:
            copy_differing_files(item, target_dir)

    return 0


if __name__ == "__main__":
    main()
