#!/usr/bin/env python3

import argparse
import glob
import os
import shutil
import sys
import time

from datetime import datetime
from pathlib import Path
from typing import List


app_version = "230117.1"

app_title = f"copydif.py (v.{app_version})"

log_file = None


def write_log(text: str):
    if log_file:
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a") as f:
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


def same_time_and_size(filename1, filename2):
    """
    Compares the file size and modified time. Returns False if either
    does not match. Also returns False if filename2 does not exist.

    Since the file modification times may have different numeric precision
    on different operating systems, strings representing the times are
    compared instead of comparing the floating point (st_mtime) values.
    """
    info1 = os.stat(filename1)
    if not os.path.exists(filename2):
        return False

    info2 = os.stat(filename2)
    if info1.st_size != info2.st_size:
        return False

    if file_time_str(info1.st_mtime) != file_time_str(info2.st_mtime):
        return False
    return True


def copy_differing_files(source_spec, target_dir):
    say(f"Source: {source_spec}")
    say(f"Target: {target_dir}")

    source_files = glob.glob(source_spec)
    if not source_files:
        say(f"No files found matching '{source_spec}'")
        return

    if len(source_files) == 1 and os.path.isdir(source_files[0]):
        source_files = glob.glob(os.path.join(source_spec, "*"))
        if not source_files:
            say(f"No files found in directory '{source_spec}'")
            return

    source_files.sort()

    for source_filename in source_files:
        target_filename = os.path.join(
            target_dir, os.path.split(source_filename)[1]
        )
        if same_time_and_size(source_filename, target_filename):
            say(f"  Same: {os.path.split(source_filename)[1]}")
        else:
            say(f"  COPY: {os.path.split(source_filename)[1]}")
            #  shutil.copy2 preserves the file modification time.
            shutil.copy2(source_filename, target_filename)


#  TODO: This script is based on an older version from the Python 2 days.
#  Is there a good reason to replace the existing os.path calls (which
#  still work) with pathlib Path methods? Not sure "because it's the new
#  thing" is a good reason. Deprecation of os.path would be a good reason.


def get_source_list(source_spec: str) -> List[str]:
    assert source_spec.startswith("@")
    file_name = source_spec.strip("@")
    say(f"Reading list-file: {file_name}")
    if not os.path.exists(file_name):
        complain(f"Cannot find source list file: '{file_name}'")
        raise SystemExit
    result = []
    with open(file_name) as f:
        lines = f.readlines()
    for line in lines:
        s = line.strip()
        #  List-file can have comments.
        if s and not s.startswith("#"):
            result.append(s)
    return result


def get_args(argv):
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

    args = ap.parse_args(argv[1:])

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
        global log_file
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


def main(argv):
    print(f"\n{app_title}\n")

    source_spec, target_dir, source_list = get_args(argv)

    write_log(app_title)

    if source_list is None:
        copy_differing_files(source_spec, target_dir)
    else:
        for item in source_list:
            copy_differing_files(item, target_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
