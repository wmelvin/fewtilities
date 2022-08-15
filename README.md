# Fewtilities

## A few utilities

This is a repository for tools that do not need a whole project structure to themselves.

---

### bymo.py

Moves files in the current directory into sub-directories named for the year and month (as *YYYY_MM*) of each file's last modified time.

```
#  /home/bill/Projects/Fewtilities/bymo.py - version 220302.1
usage: bymo.py [-h] [-m] [-k] [filespecs [filespecs ...]]

Move files in the current directory (folder) to sub-directories named for the
year and month the file was last modified.

positional arguments:
  filespecs          Optional file specification for matching files to move
                     (ie. '*.jpg').

optional arguments:
  -h, --help         show this help message and exit
  -m, --move-now     Move the files now. By default, the commands are printed
                     but not executed.
  -k, --keep-spaces  Keep spaces in destination file names. By default, spaces
                     are replaced with underscores.
```

---

### csv_to_md.py

Reads a CSV file and writes the data as a Markdown table.

```
usage: csv_to_md.py [-h] csv_file

Read a CSV file and write a Markdown table.

positional arguments:
  csv_file    Path to CSV file.

optional arguments:
  -h, --help  show this help message and exit
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
#  /home/bill/Projects/Fewtilities/scren.py - version 220815.1
usage: scren.py [-h] [-s SEARCH_DIR] [-m] [--what-if]

Rename screenshot files. Finds files matching patterns for screenshot file
names and moves (renames) them. By default the current directory is searched
and a prompt is displayed asking whether the file should be moved. The default
answer is Yes (Y) if Enter is pressed without any other input. The prompt also
includes the option to move all files (A), or to quit (Q). Search is not
recursive (sub-directories are not searched).

optional arguments:
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
