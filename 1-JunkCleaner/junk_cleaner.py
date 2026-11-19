import os
import platform
import stat
import tempfile
import time
from pathlib import Path

try:
    import fcntl
except ImportError:
    fcntl = None

TEMP_DAYS = 7
VAR_TMP_DAYS = 30
CACHE_DAYS = 30
DAY = 86400


def get_temp_folders():
    folders = []
    system = platform.system()
    home = Path.home()

    if system == "Windows":
        for name in ("TEMP", "TMP"):
            value = os.environ.get(name)
            if value:
                folders.append((Path(value), TEMP_DAYS))
        local = os.environ.get("LOCALAPPDATA")
        if local:
            folders.append((Path(local) / "Temp", TEMP_DAYS))
        windir = os.environ.get("WINDIR")
        if windir:
            folders.append((Path(windir) / "Temp", TEMP_DAYS))
    elif system == "Darwin":
        folders.append((Path("/tmp"), TEMP_DAYS))
        folders.append((Path("/private/tmp"), TEMP_DAYS))
        folders.append((home / "Library" / "Caches", CACHE_DAYS))
    else:
        folders.append((Path("/tmp"), TEMP_DAYS))
        folders.append((Path("/var/tmp"), VAR_TMP_DAYS))
        folders.append((home / ".cache", CACHE_DAYS))

    folders.append((Path(tempfile.gettempdir()), TEMP_DAYS))

    found = []
    seen = set()
    for folder, days in folders:
        try:
            key = folder.resolve()
        except OSError:
            key = folder
        if folder.is_dir() and key not in seen:
            seen.add(key)
            found.append((folder, days))
    return found


def open_inodes():
    found = set()
    if platform.system() != "Linux":
        return found
    try:
        pids = os.listdir("/proc")
    except OSError:
        return found
    for pid in pids:
        if not pid.isdigit():
            continue
        try:
            fds = os.listdir("/proc/" + pid + "/fd")
        except OSError:
            continue
        for fd in fds:
            try:
                info = os.stat("/proc/" + pid + "/fd/" + fd)
            except OSError:
                continue
            found.add((info.st_dev, info.st_ino))
    return found


def is_locked(path):
    if fcntl is None:
        return False
    try:
        with open(path, "rb") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return True
    except OSError:
        return False
    return False


def find_junk(folders, open_set):
    junk = []
    skipped = {"new": 0, "used": 0, "other": 0}
    now = time.time()
    for folder, days in folders:
        cutoff = days * DAY
        try:
            paths = folder.rglob("*")
        except (OSError, PermissionError):
            continue
        for item in paths:
            try:
                if item.is_symlink():
                    skipped["other"] += 1
                    continue
                info = item.stat(follow_symlinks=False)
            except (OSError, PermissionError):
                skipped["other"] += 1
                continue
            if not stat.S_ISREG(info.st_mode):
                skipped["other"] += 1
                continue
            if hasattr(os, "getuid") and info.st_uid != os.getuid():
                skipped["other"] += 1
                continue
            newest = max(info.st_mtime, info.st_atime)
            if (now - newest) <= cutoff:
                skipped["new"] += 1
                continue
            if (info.st_dev, info.st_ino) in open_set:
                skipped["used"] += 1
                continue
            if is_locked(item):
                skipped["used"] += 1
                continue
            junk.append(item)
    return junk, skipped


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
    locked = 0
    for item in files:
        try:
            size = item.stat().st_size
            item.unlink()
            freed += size
            deleted += 1
        except (OSError, PermissionError):
            locked += 1
            continue
    print("Deleted", deleted, "files.")
    if locked:
        print("Skipped", locked, "files that were in use.")
    return freed / 1024 / 1024


def main():
    print("Junk Cleaner")
    print("System:", platform.system())
    print()

    folders = get_temp_folders()
    print("Checking these folders:")
    for folder, days in folders:
        print("  ", folder, "- files older than", days, "days")
    print()

    open_set = open_inodes()
    junk, skipped = find_junk(folders, open_set)
    size = file_size_mb(junk)
    print("Found", len(junk), "files,", round(size, 2), "MB in total.")
    total = skipped["new"] + skipped["used"] + skipped["other"]
    if total:
        print(
            "Skipped",
            total,
            "files (too new:",
            skipped["new"],
            ", in use:",
            skipped["used"],
            ", other:",
            skipped["other"],
            ").",
        )
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
