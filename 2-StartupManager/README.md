# Startup Manager - Tool 2

Lists the apps that start when you log in, on
Windows, Mac, and Linux.

## Run it

Windows: double-click `run.bat`
Mac / Linux: double-click `run.sh`, or in a terminal run:
`python3 startup_manager.py`

You need Python 3. Get it from python.org if you do not have it.

## What it does

1. Lists the apps that start at login.
2. You type the numbers to turn off, like 1,3.
3. It asks you to type `yes` before it changes anything.
4. Turning one off does not delete the app.
   It only stops it starting by itself.
   Files are renamed to `.disabled`, so you can
   turn them back on by removing `.disabled`.
