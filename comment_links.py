#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import NamedTuple

DEFAULT_FILENAME = "comment_links.html"

app_version = "2024.02.1"

app_title = f"comment_links.py (v{app_version})"

run_dt = datetime.now()


class AppOptions(NamedTuple):
    source_files: list[Path]
    out_file: Path


def html_style():
    s = """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 1rem 4rem;
        }
        h1 {
            color: darkgray;
        }
        a:link, a:visited {
            color: #00248F;
            text-decoration: none;
        }
        :link:hover,:visited:hover {
            color: #B32400;
            text-decoration: underline;
        }
        #footer {
            border-top: 1px solid black;
            font-size: x-small;
            margin-top: 2rem;
        }
        .item {
            margin-top: 1.0rem;
        }
        .comment-context {
            color: gray;
            font-size: small;
        }
    """
    return s.lstrip("\n").rstrip()


def html_head(title):
    return (
        dedent(
            """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta name="generator" content="{0}">
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <title>{1}</title>
            <style>
        {2}
            </style>
            <base target="_blank">
        </head>
        <body>
        <h1>{1}</h1>
        """
        )
        .format(app_title, title, html_style())
        .strip("\n")
    )


def html_tail():
    return dedent(
        """
        <div id="footer">
          Created {0} by {1}
        </div>
        </body>
        </html>
        """
    ).format(run_dt.strftime("%Y-%m-%d %H:%M"), app_title)


def get_args(arglist=None):
    ap = argparse.ArgumentParser(
        description="Extract links from comments in a script. This tool only "
        "works with scripts, such as Python or PowerShell, that use the '#' "
        "symbol for comments."
    )

    ap.add_argument(
        "source_files",
        nargs="+",
        action="store",
        help="Script file to read.",
    )

    ap.add_argument(
        "-o",
        "--output-dir",
        type=str,
        dest="out_dir",
        default=str(Path.cwd()),
        action="store",
        help="Directory in which to create the output file. Optional. "
        "By default, output is written to the current directory.",
    )

    ap.add_argument(
        "-n",
        "--out-name",
        type=str,
        dest="out_name",
        default=DEFAULT_FILENAME,
        action="store",
        help=f"Output file name. Optional. Default is {DEFAULT_FILENAME}.",
    )

    ap.add_argument(
        "--no-dt",
        dest="no_dt",
        action="store_true",
        help="Do not add the date_time tag, which is added by default, to the "
        "output file name. Optional.",
    )

    return ap.parse_args(arglist)


def get_opts(arglist=None):
    args = get_args(arglist)

    source_files = []
    for fn in args.source_files:
        source_file = Path(fn).expanduser().resolve()
        if source_file.exists() and source_file.is_file():
            source_files.append(source_file)
        else:
            sys.stderr.write(f"\nERROR: Cannot find file '{source_file}'.\n")
            sys.exit(1)

    out_dir = Path(args.out_dir).expanduser().resolve()

    if not (out_dir.exists() and out_dir.is_dir()):
        sys.stderr.write(f"\nERROR: Cannot find directory '{out_dir}'.\n")
        sys.exit(1)

    dt = "" if args.no_dt else f"-{run_dt.strftime('%y%m%d_%H%M%S')}"

    p = Path(args.out_name)
    fn = f"{p.stem}{dt}.html"

    out_file = out_dir.joinpath(fn)

    return AppOptions(source_files, out_file)


def link_html(url, context_before, context_after):
    assert isinstance(context_before, list)  # noqa: S101
    assert isinstance(context_after, list)  # noqa: S101

    result = '<div class="item">\n'
    for item in context_before:
        #  Only include non-empty comment lines in the context.
        ctx: str = item.strip()
        if ctx.startswith("#") and ctx.replace("#", ""):
            result += f'  <span class="comment-context">{item}</span><br>\n'

    result += f'  <a href="{url}">{url}</a><br>\n'

    for item in context_after:
        ctx: str = item.strip()
        if ctx.startswith("#") and ctx.replace("#", ""):
            result += f'  <span class="comment-context">{item}</span><br>\n'
    result += "</div>\n"
    return result


def get_comment_links(source_file: Path) -> str:
    print(f"Reading '{source_file}'")

    with source_file.open() as f:
        lines = f.readlines()

    result = ""

    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("#") and ("https://" in s or "http://" in s):
            #  Remove leading comment chars and spaces, and trailing
            #  whitespace.
            url = s.lstrip("# ").rstrip()

            #  Split on space char and take the first element to remove any
            #  text after the URL.
            usplit = url.split(" ")
            url = usplit[0]

            # Get context lines before and after the current line.
            ctx1 = lines[i - 2 : i]
            ctx2 = lines[i + 1 : i + 3]

            result += link_html(url, ctx1, ctx2)

    if result:
        result = f"<p>From: <strong>{source_file.name}</strong></p>\n{result}"
    else:
        print(f"  No links in '{source_file.name}'")

    return result


def main(arglist=None):
    print(f"\n{app_title}\n")

    opts = get_opts(arglist)

    body = ""
    for source_file in opts.source_files:
        body += get_comment_links(source_file)

    print(f"Writing '{opts.out_file}'")

    with opts.out_file.open("w") as html:
        html.write(f'{html_head("comment_links")}\n')
        html.write(body)
        html.write(f"{html_tail()}\n")

    print("Done.")
    return 0


if __name__ == "__main__":
    main()
