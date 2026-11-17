import shutil
from pathlib import Path

CATEGORIES = {
    "Images": {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".webp",
        ".svg",
        ".heic",
    },
    "Documents": {
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".md",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".csv",
        ".epub",
        ".odt",
    },
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv"},
    "Music": {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".dmg"},
    "Code": {".py", ".js", ".html", ".css", ".cpp", ".c", ".java", ".json"},
}

SKIP = {".crdownload", ".part", ".partial", ".tmp"}


def category_for(path):
    suffix = path.suffix.lower()
    for name, suffixes in CATEGORIES.items():
        if suffix in suffixes:
            return name
    return "Others"


def free_name(folder, name):
    target = folder / name
    if not target.exists():
        return target
    stem = Path(name).stem
    suffix = Path(name).suffix
    number = 1
    while True:
        target = folder / (stem + " (" + str(number) + ")" + suffix)
        if not target.exists():
            return target
        number += 1


def main():
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
    print("This moves", len(moves), "files. Nothing is deleted.")
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
