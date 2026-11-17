import os
import platform
import tempfile
from pathlib import Path


def get_temp_folders():
    folders = []
    system = platform.system()
    home = Path.home()

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
        folders.append(home / "Library" / "Caches")
    else:
        folders.append(Path("/tmp"))
        folders.append(Path("/var/tmp"))
        folders.append(home / ".cache")

    folders.append(Path(tempfile.gettempdir()))

    found = []
    for folder in folders:
        if folder.is_dir() and folder not in found:
            found.append(folder)
    return found


def find_junk(folders):
    junk = []
    for folder in folders:
        try:
            files = folder.rglob("*")
        except (OSError, PermissionError):
            continue
        for item in files:
            try:
                if item.is_file():
                    junk.append(item)
            except (OSError, PermissionError):
                continue
    return junk


def file_size_mb(files):
    total = 0
    for item in files:
        try:
            total += item.stat().st_size
        except (OSError, PermissionError):
            continue
    return total / 1024 / 1024


def delete_files(files):
    freed = 0
    deleted = 0
    for item in files:
        try:
            size = item.stat().st_size
            item.unlink()
            freed += size
            deleted += 1
        except (OSError, PermissionError):
            continue
    print("Deleted", deleted, "files.")
    return freed / 1024 / 1024


def main():
    print("Junk Cleaner")
    print("System:", platform.system())
    print()

    folders = get_temp_folders()
    print("Checking these folders:")
    for folder in folders:
        print("  ", folder)
    print()

    junk = find_junk(folders)
    size = file_size_mb(junk)
    print("Found", len(junk), "files,", round(size, 2), "MB in total.")
    print()

    if not junk:
        print("Nothing to clean.")
        return

    print("First 20 files:")
    for item in junk[:20]:
        print("  ", item)
    if len(junk) > 20:
        print("  ... and", len(junk) - 20, "more.")
    print()

    answer = input("Delete these files? Type yes to go: ")
    if answer.strip().lower() != "yes":
        print("Stopped. Nothing was deleted.")
        return

    freed = delete_files(junk)
    print("Done. Freed", round(freed, 2), "MB.")


if __name__ == "__main__":
    main()
