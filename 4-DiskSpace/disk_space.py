#!/usr/bin/env python3
"""Disk Space Analyser - Tool 4 of the PC Tools Pack.

Shows how much space you have left, which
folders are using the most space, which files
are the biggest, and which file types use
the most space.

How to run:
    Windows: py disk_space.py
    Mac / Linux: python3 disk_space.py

Safety:
    - It only shows facts, no warnings or
      fake errors.
    - Delete is optional. After the list, you
      can pick big files to delete, by number.
      It shows them first, then asks you to
      type yes. Files only, never folders.

GitHub patterns used, not copied whole:
    - gccszs/disk-cleaner, analyze_disk.py:
      read-only disk analysis, largest
      directories, largest files, disk
      usage with shutil.disk_usage.
      https://github.com/gccszs/disk-cleaner
    - MrHakan/FolderLens:
      largest files list, folder sizes,
      disk usage shown as free / total.
      https://github.com/MrHakan/FolderLens
    - Muphan/Disk-Space-Analyzer:
      top 10 largest folders and files.
      https://github.com/Muphan/
      Disk-Space-Analyzer
"""

import shutil
from collections import Counter
from pathlib import Path


def show_size(size):
    """Show a size in GB, MB, or KB."""
    if size >= 1024 * 1024 * 1024:
        return str(round(size / 1024 ** 3, 2)) + " GB"
    if size >= 1024 * 1024:
        return str(round(size / 1024 ** 2, 1)) + " MB"
    if size >= 1024:
        return str(round(size / 1024, 1)) + " KB"
    return str(size) + " B"


def folder_size(folder):
    """Add up the size of all files in a folder."""
    total = 0
    for path in folder.rglob("*"):
        if path.is_file():
            try:
                total += path.stat().st_size
            except OSError:
                continue
    return total


def main():
    """Show drive space, biggest folders and files."""
    print("Disk Space Analyser")
    print()

    text = input("Folder to check? Press Enter for "
                 "your home folder: ")
    if text.strip():
        folder = Path(text.strip()).expanduser()
    else:
        folder = Path.home()
    if not folder.is_dir():
        print("That folder does not exist.")
        return

    print("Checking:", folder)
    print()

    total, used, free = shutil.disk_usage(folder)
    print("Drive space:")
    print("  Total:", show_size(total))
    print("  Used: ", show_size(used),
          "-", round(used / total * 100, 1), "%")
    print("  Free: ", show_size(free),
          "-", round(free / total * 100, 1), "%")
    print()

    print("Biggest folders in", folder, ":")
    folders = []
    for child in folder.iterdir():
        if child.is_dir():
            size = folder_size(child)
            folders.append((child, size))
    folders.sort(key=lambda item: item[1], reverse=True)
    if not folders:
        print("  None found.")
    for path, size in folders[:10]:
        print("  ", show_size(size), "-", path.name)
    print()

    print("Biggest files:")
    files = []
    for path in folder.rglob("*"):
        if path.is_file():
            try:
                files.append((path, path.stat().st_size))
            except OSError:
                continue
    files.sort(key=lambda item: item[1], reverse=True)
    top_files = files[:10]
    if not top_files:
        print("  None found.")
    for number, (path, size) in enumerate(top_files, 1):
        print("  ", number, "-", show_size(size), "-", path)
    print()

    print("Space by file type:")
    types = Counter()
    for path, size in files:
        suffix = path.suffix.lower() or "(no type)"
        types[suffix] += size
    for suffix, size in types.most_common(10):
        print("  ", show_size(size), "-", suffix)
    print()

    if not top_files:
        print("Done. Nothing was deleted.")
        return

    answer = input("Delete any of the big files above? "
                   "Type numbers, like 1,3, or press "
                   "Enter to keep everything: ")
    if not answer.strip():
        print("Done. Nothing was deleted.")
        return

    picks = []
    for part in answer.split(","):
        part = part.strip()
        if part.isdigit():
            number = int(part)
            if 1 <= number <= len(top_files):
                picks.append(top_files[number - 1])

    if not picks:
        print("No valid numbers. Nothing was deleted.")
        return

    print()
    print("You picked:")
    for path, size in picks:
        print("  ", show_size(size), "-", path)
    print()

    confirm = input("Delete these files? Type yes to go: ")
    if confirm.strip().lower() != "yes":
        print("Stopped. Nothing was deleted.")
        return

    freed = 0
    done = 0
    for path, size in picks:
        try:
            path.unlink()
            freed += size
            done += 1
            print("Deleted:", path)
        except OSError:
            print("Could not delete:", path)
    print("Deleted:", done, "files, freed",
          show_size(freed))
    print("Done.")


if __name__ == "__main__":
    main()
