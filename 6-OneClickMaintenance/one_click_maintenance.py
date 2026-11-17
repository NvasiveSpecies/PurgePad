#!/usr/bin/env python3
"""One-Click Maintenance - Tool 6.

Does the safe clean-up jobs in one go, with
one yes at the start:
    1. Cleans temp and junk files.
    2. Shows how much free space you have.
    3. Counts the apps that start at login.

How to run:
    Windows: py one_click_maintenance.py
    Mac / Linux: python3 one_click_maintenance.py

Safety:
    - Shows a preview first, asks you to
      type yes once before deleting anything.
    - Deletes temp files only, never folders,
      never your documents or photos.
    - Does not turn off startup apps, it
      only counts them. Use Tool 2 to turn
      one off.
    - No registry cleaner, no driver updater,
      no RAM booster, no speed promises.
      Only real numbers: files deleted and
      space freed.

GitHub patterns used, not copied whole:
    - Darkos-Windows-Utility-Tool-DWUT:
      one-click tune-up in a safe order,
      clean temp files first, show freed
      space per file.
      https://github.com/Darko-Development/
      Darkos-Windows-Utility-Tool-DWUT
    - krezio/roomy:
      read-only scan first, nothing deleted
      until you click clean up, safe files
      only.
      https://github.com/krezio/roomy
    - jothank/pitcrew:
      cleanup with sizes shown first,
      facts only, no score.
      https://github.com/jothank/pitcrew
"""

import os
import platform
import shutil
import tempfile
from pathlib import Path


def show_size(size):
    """Show a size in MB, with one decimal."""
    return str(round(size / 1024 / 1024, 1)) + " MB"


def get_temp_folders():
    """Return the temp folders for this system."""
    folders = []
    system = platform.system()
    if system == "Windows":
        for name in ("TEMP", "TMP"):
            value = os.environ.get(name)
            if value:
                folders.append(Path(value))
        local = os.environ.get("LOCALAPPDATA")
        if local:
            folders.append(Path(local) / "Temp")
        windir = os.environ.get("WINDIR")
        if windir:
            folders.append(Path(windir) / "Temp")
    elif system == "Darwin":
        folders.append(Path("/tmp"))
        folders.append(Path("/private/tmp"))
        folders.append(Path.home() / "Library" / "Caches")
    else:
        folders.append(Path("/tmp"))
        folders.append(Path("/var/tmp"))
        folders.append(Path.home() / ".cache")
    folders.append(Path(tempfile.gettempdir()))
    seen = []
    for folder in folders:
        if folder.is_dir() and folder not in seen:
            seen.append(folder)
    return seen


def count_startup():
    """Count startup apps, without changing them."""
    system = platform.system()
    if system == "Linux":
        folder = Path.home() / ".config" / "autostart"
        if folder.is_dir():
            return len(list(folder.glob("*.desktop")))
        return 0
    if system == "Darwin":
        folder = Path.home() / "Library" / "LaunchAgents"
        if folder.is_dir():
            return len(list(folder.glob("*.plist")))
        return 0
    appdata = os.environ.get("APPDATA")
    if appdata:
        folder = Path(appdata) / "Microsoft" / "Windows"
        folder = folder / "Start Menu" / "Programs"
        folder = folder / "Startup"
        if folder.is_dir():
            return len(list(folder.iterdir()))
    return 0


def main():
    """Preview, ask once, then clean temp files."""
    print("One-Click Maintenance")
    print("System:", platform.system())
    print()

    total, used, free = shutil.disk_usage(Path.home())
    print("Free space before:", show_size(free))
    print()

    folders = get_temp_folders()
    junk = []
    for folder in folders:
        for path in folder.rglob("*"):
            if path.is_file():
                try:
                    junk.append((path, path.stat().st_size))
                except OSError:
                    continue

    size = sum(item[1] for item in junk)
    print("Temp files found:", len(junk),
          "-", show_size(size))
    for path, item_size in junk[:10]:
        print("  ", show_size(item_size), "-", path)
    if len(junk) > 10:
        print("  ... and", len(junk) - 10, "more")
    print()

    if not junk:
        print("Nothing to clean.")
    else:
        answer = input("Clean these temp files? "
                       "Type yes to go: ")
        if answer.strip().lower() != "yes":
            print("Stopped. Nothing was deleted.")
            return
        freed = 0
        done = 0
        for path, item_size in junk:
            try:
                path.unlink()
                freed += item_size
                done += 1
            except OSError:
                continue
        print("Deleted:", done, "files, freed",
              show_size(freed))
    print()

    print("Startup apps at login:", count_startup())
    print("Use Tool 2 if you want to turn one off.")
    print()

    total, used, free = shutil.disk_usage(Path.home())
    print("Free space now:", show_size(free))
    print("Done.")


if __name__ == "__main__":
    main()
