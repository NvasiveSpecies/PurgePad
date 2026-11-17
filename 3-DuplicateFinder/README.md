# Duplicate and Large-File Finder - Tool 3

Finds big files over 100 MB, and finds exact
duplicate files.

## Run it

Windows: double-click `run.bat`
Mac / Linux: double-click `run.sh`, or in a terminal run:
`python3 duplicate_finder.py`

You need Python 3. Get it from python.org if you do not have it.

## What it does

1. Asks for a folder, or press Enter for your home folder.
2. Lists the biggest files over 100 MB. It never deletes those.
3. Finds exact duplicates by size and by full SHA-256 hash.
4. Keeps the first copy, and asks you to type `yes`
   before it deletes any extra copies.
