#!/usr/bin/env python3

import argparse
import sys

from collections import namedtuple
from datetime import datetime
from pathlib import Path
from textwrap import dedent


DEFAULT_FILENAME = "comment_links.html"


app_version = "230121.1"

app_title = f"comment_links.py (v.{app_version})"

run_dt = datetime.now()


AppOptions = namedtuple("AppOptions", "source_file, out_file")


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
          Created {0} by {1}.
        </div>
        </body>
        </html>
        """
    ).format(run_dt.strftime("%Y-%m-%d %H:%M"), app_title)


def get_args(argv):
    ap = argparse.ArgumentParser(
        description="Extract links from comments in a script."
    )

    ap.add_argument(
        "source_file",
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

    return ap.parse_args(argv[1:])


def get_opts(argv):
    args = get_args(argv)

    source_file = Path(args.source_file).expanduser().resolve()

    # TODO: Handle errors.
    assert source_file.exists()
    assert source_file.is_file()

    out_dir = Path(args.out_dir).expanduser().resolve()

    # TODO: Handle errors.
    assert out_dir.exists()
    assert out_dir.is_dir()

    if args.no_dt:
        dt = ""
    else:
        dt = f"-{run_dt.strftime('%y%m%d_%H%M%S')}"

    p = Path(args.out_name)
    fn = f"{p.stem}{dt}.html"

    out_file = out_dir.joinpath(fn)

    return AppOptions(source_file, out_file)


def link_html(url, context_before, context_after):
    assert isinstance(context_before, list)
    assert isinstance(context_after, list)

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


def main(argv):
    print(f"\n{app_title}\n")

    opts = get_opts(argv)
    assert isinstance(opts.source_file, Path)
    assert isinstance(opts.out_file, Path)

    print(f"Reading {opts.source_file}")

    with open(opts.source_file) as f:
        lines = f.readlines()

    print(f"Writing {opts.out_file}")

    with open(opts.out_file, "w") as html:
        html.write(f'{html_head("comment_links")}\n')

        html.write(f'<p>From: <strong>{opts.source_file}</strong></p>\n')

        for i, line in enumerate(lines):
            s = line.strip()
            if s.startswith("#") and ("https://" in s or "http://" in s):
                #  Remove comment char and any space after it.
                url = s[1:].strip()

                #  Split on space char and take the first element to remove any
                #  text after the URL.
                usplit = url.split(" ")
                url = usplit[0]

                # Get context lines before and after the current line.
                ctx1 = lines[i-2:i]
                ctx2 = lines[i+1:i+3]

                html.write(link_html(url, ctx1, ctx2))

        html.write(f"{html_tail()}\n")

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
