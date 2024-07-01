# Fewtilities

## A few utilities

This is a repository for some command-line tools that do not need a whole project structure for each one individually. These are **Python** scripts that use only **standard library modules**. Any additional requirements are only for development and testing.

[bymo.py](#bymopy) - Move files into sub-directories named for the year and month.

[comment\_links.py](#comment_linkspy) - Extract links from comments in a script and into a new HTML file.

[copydif.py](#copydifpy) - Copy files that differ from a source directory to a target directory (one-way sync).

[csv\_to\_md.py](#csv_to_mdpy) - Read a CSV file and write the data as a Markdown table.

[from\_today.py](#from_todaypy) - Print a set of future dates, *n* days from today.

[scren.py](#screnpy) - Rename captured screenshot files to a more compact name.

---

### bymo.py

Moves files in the current directory into sub-directories named for the year and month (as *YYYY_MM*) of each file's last modified time.

```
usage: bymo.py [-h] [-m] [-k] [--by-year] [--what-if] [filespecs ...]

Move files in the current directory (folder) to sub-directories named for the
year and month the file was last modified.

positional arguments:
  filespecs          Optional file specification for matching files to move
                     (ie. '*.jpg').

options:
  -h, --help         show this help message and exit
  -m, --move-now     Move the files now. By default, the commands are printed
                     but not executed.
  -k, --keep-spaces  Keep spaces in destination file names. By default, spaces
                     are replaced with underscores.
  --by-year          Move files to sub-directories named for only the year the
                     file was last modified (instead of year and month which
                     is the default action).
  --what-if          Print the list of files that would be moved.
```

---

### comment_links.py

Extract **links** (strings that start with "https://" or "http://") from **comments** (strings that start with "#") in a script file (such as Python or PowerShell) and create a HTML file containing those links (with a few lines of surrounding context). This is to make it easier to review, collect, and summarize such links.

Currently, this is limited to scripts that use "#" for comments.

```
usage: comment_links.py [-h] [-o OUT_DIR] [-n OUT_NAME] [--no-dt]
                        source_files [source_files ...]

Extract links from comments in a script. This tool only works with scripts,
such as Python or PowerShell, that use the '#' symbol for comments.

positional arguments:
  source_files          Script file to read.

options:
  -h, --help            show this help message and exit
  -o OUT_DIR, --output-dir OUT_DIR
                        Directory in which to create the output file.
                        Optional. By default, output is written to the current
                        directory.
  -n OUT_NAME, --out-name OUT_NAME
                        Output file name. Optional. Default is
                        comment_links.html.
  --no-dt               Do not add the date_time tag, which is added by
                        default, to the output file name. Optional.
```

---

### copydif.py

Copy differing files from a source directory (or wildcard pattern) to a target directory. This a basically a one-way file synchronization that does not mirror the source (extra files in the target location are not deleted).

This script was created to update local copies, on multiple machines, by pulling from a source location on a file server - a simple local deployment of tools and utilities.

For more options, use [rsync](https://en.wikipedia.org/wiki/Rsync) or [Robocopy](https://en.wikipedia.org/wiki/Robocopy) (Windows) instead of this script. ;-)

```
usage: copydif.py [-h] [--log-file LOG_FILE] source_spec target_dir

Copy only files that have different sizes or modification times, or are not
present in the target directory. This will overwrite a newer file in the
target directory with an older file from the source directory (rollback).

positional arguments:
  source_spec          Source directory or file specification. This can be the
                       path for a single file. It can also include a wilcard
                       character to match multiple files ('source/path/*.txt'
                       for example). If a directory name is given then all
                       files in the directory are included, but sub-
                       directories are not. This script does not do recursive
                       processing of sub-directories. The source can also be a
                       list file (a text file with the path to a source file
                       on each line) if the file name is prefixed with an '@'
                       symbol.
  target_dir           Directory to update with any changed files.

options:
  -h, --help           show this help message and exit
  --log-file LOG_FILE  Name of the log file to create (or append, if exists).
                       By default, there is no log file.
```

---

### csv_to_md.py

Reads a CSV file and writes the data as a Markdown table.

```
usage: csv_to_md.py [-h] [--no-info] [--no-source] [-n MD_FILE] [--force]
                    csv_file

Read a CSV file and write a Markdown table.

positional arguments:
  csv_file              Path to CSV file.

options:
  -h, --help            show this help message and exit
  --no-info             Do not include the 'Created by...' information header.
  --no-source           Do not include the 'Source:...' header.
  -n MD_FILE, --name MD_FILE
                        Name of the output file to create. Optional. By
                        default the output file is named using the name of the
                        input (CSV) file with a date_time tag and a '.md'
                        suffix. An existing file with the same name will not
                        be overwritten unless the --force option is used.
  --force               Allow an existing output file to be overwritten.
```

This requires that the CSV file is formatted as a table, with a single heading row, with unique column titles, followed by data rows.

---

### from_today.py

Prints future dates for a list of days from today.

The initial purpose of this script is to calculate options for the date to use when labelling a "keep until" folder.

---

### scren.py

Renames screenshot files in the current directory to a shorter file name.

```
usage: scren.py [-h] [-s SEARCH_DIR] [-m] [--what-if]

Rename screenshot files. Finds files matching patterns for screenshot file
names and moves (renames) them. By default the current directory is searched
and a prompt is displayed asking whether the file should be moved. The default
answer is Yes (Y) if Enter is pressed without any other input. The prompt also
includes the option to move all files (A), or to quit (Q). Search is not
recursive (sub-directories are not searched).

options:
  -h, --help            show this help message and exit
  -s SEARCH_DIR, --search-dir SEARCH_DIR
                        Search the given directory, instead of the current
                        directory, for screenshot files. Search is not
                        recursive (sub-directories are not searched).
  -m, --move-now        Move the files now instead of prompting whether to
                        move each file.
  --what-if             Print the list of files that would be moved.
```

---
