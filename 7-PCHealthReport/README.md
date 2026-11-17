# PC Health Report - Tool 7

Prints a plain report of facts about your
computer, and saves it to a text file.

## Run it

Windows: double-click `run.bat`
Mac / Linux: double-click `run.sh`, or in a terminal run:
`python3 pc_health_report.py`

You need Python 3. Get it from python.org if you do not have it.

## What it shows

- System, version, processor, CPU cores, Python version
- Memory total and free, where it can be read
- Drive total, used, and free space
- Temp files: how many, and how big
- Startup apps: how many
- Downloads and Desktop: how many files

Read-only. It does not delete or change anything.
No score, no warnings, no fake errors.
The report is saved to `pc_health_report.txt`
in the same folder.
