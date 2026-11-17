#!/usr/bin/env python3
"""Downloads and Desktop Organizer - Tool 5.

Sorts the loose files in Downloads or on
your Desktop into folders by type: Images,
Documents, Videos, Music, Archives, Code,
and Others.

How to run:
    Windows: py file_organizer.py
    Mac / Linux: python3 file_organizer.py

Safety:
    - Shows a preview first, asks you to
      type yes before moving anything.
    - Moves files only, never deletes them.
    - Only moves top-level files, it leaves
      folders alone.
    - Skips files still downloading:
      .crdownload, .part, .partial, .tmp
    - If a file with the same name is already
      there, it adds (1), (2), and so on.
      It never overwrites a file.

GitHub patterns used, not copied whole:
    - Cosmosynth/DownLSort:
      sort by category, preview first,
      confirm, then move, never overwrite.
      https://github.com/Cosmosynth/DownLSort
    - MRAVLM/Smart-File-Organizer:
      extension table, Images, Documents,
      Videos, Music, Code, Archives, Others.
      https://github.com/MRAVLM/
      smart-file-organizer
    - eericstephh/SmartSort:
      never overwrite, conflicts become
      photo (1).jpg, skip in-progress files.
      https://github.com/eericstephh/SmartSort
"""

import shutil
from pathlib import Path


CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif",
               ".bmp", ".webp", ".svg", ".heic"},
    "Documents": {".pdf", ".doc", ".docx", ".txt",
                  ".md", ".xls", ".xlsx", ".ppt",
                  ".pptx", ".csv", ".epub", ".odt"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov",
               ".webm", ".wmv", ".flv"},
    "Music": {".mp3", ".wav", ".flac", ".m4a",
              ".aac", ".ogg", ".wma"},
    "Archives": {".zip", ".rar", ".7z", ".tar",
                 ".gz", ".iso", ".dmg"},
    "Code": {".py", ".js", ".html", ".css",
             ".cpp", ".c", ".java", ".json"},
}

SKIP = {".crdownload", ".part", ".partial", ".tmp"}


def category_for(path):
    """Return the folder name for a file."""
    suffix = path.suffix.lower()
    for name, suffixes in CATEGORIES.items():
        if suffix in suffixes:
            return name
    return "Others"


def free_name(folder, name):
    """Find a free name, adding (1), (2) if needed."""
    target = folder / name
    if not target.exists():
        return target
    stem = Path(name).stem
    suffix = Path(name).suffix
    number = 1
    while True:
        target = folder / (stem + " (" + str(number) +
                           ")" + suffix)
        if not target.exists():
            return target
        number += 1


def main():
    """Preview the moves, ask, then move files."""
    print("Downloads and Desktop Organizer")
    print()
    print("1 - Downloads")
    print("2 - Desktop")
    print("3 - Another folder")
    print()

    choice = input("Pick 1, 2, or 3: ").strip()
    if choice == "1":
        folder = Path.home() / "Downloads"
    elif choice == "2":
        folder = Path.home() / "Desktop"
    elif choice == "3":
        text = input("Folder to organize: ").strip()
        folder = Path(text).expanduser()
    else:
        print("That is not 1, 2, or 3. Stopped.")
        return

    if not folder.is_dir():
        print("That folder does not exist:", folder)
        return

    moves = []
    for path in sorted(folder.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() in SKIP:
            continue
        target_folder = folder / category_for(path)
        moves.append((path, target_folder))

    if not moves:
        print("Nothing to organize in:", folder)
        return

    print()
    print("Plan:")
    for path, target_folder in moves:
        print("  ", path.name, "->", target_folder.name)
    print()
    print("This moves", len(moves), "files. "
          "Nothing is deleted.")
    print()

    answer = input("Move these files? Type yes to go: ")
    if answer.strip().lower() != "yes":
        print("Stopped. Nothing was moved.")
        return

    done = 0
    for path, target_folder in moves:
        target_folder.mkdir(exist_ok=True)
        target = free_name(target_folder, path.name)
        try:
            shutil.move(str(path), str(target))
            done += 1
        except OSError:
            print("Could not move:", path)
    print("Moved:", done, "files.")
    print("Done.")


if __name__ == "__main__":
    main()
