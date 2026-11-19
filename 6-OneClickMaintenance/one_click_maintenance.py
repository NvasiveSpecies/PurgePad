import os
import platform
import shutil
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


def show_size(size):
    return str(round(size / 1024 / 1024, 1)) + " MB"


def get_temp_folders():
    folders = []
    system = platform.system()
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
        folders.append((Path.home() / "Library" / "Caches", CACHE_DAYS))
    else:
        folders.append((Path("/tmp"), TEMP_DAYS))
        folders.append((Path("/var/tmp"), VAR_TMP_DAYS))
        folders.append((Path.home() / ".cache", CACHE_DAYS))
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
            junk.append((item, info.st_size))
    return junk, skipped


def count_startup():
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
    print("One-Click Maintenance")
    print("System:", platform.system())
    print()

    _total, _used, free = shutil.disk_usage(Path.home())
    print("Free space before:", show_size(free))
    print()

    folders = get_temp_folders()
    open_set = open_inodes()
    junk, skipped = find_junk(folders, open_set)

    size = sum(item[1] for item in junk)
    print("Temp files found:", len(junk), "-", show_size(size))
    for path, item_size in junk[:10]:
        print("  ", show_size(item_size), "-", path)
    if len(junk) > 10:
        print("  ... and", len(junk) - 10, "more")
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
    else:
        answer = input("Clean these temp files? Type yes to go: ")
        if answer.strip().lower() != "yes":
            print("Stopped. Nothing was deleted.")
            return
        freed = 0
        done = 0
        locked = 0
        for path, item_size in junk:
            try:
                path.unlink()
                freed += item_size
                done += 1
            except OSError:
                locked += 1
                continue
        print("Deleted:", done, "files, freed", show_size(freed))
        if locked:
            print("Skipped", locked, "files that were in use.")
    print()

    print("Startup apps at login:", count_startup())
    print("Use Tool 2 if you want to turn one off.")
    print()

    _total, _used, free = shutil.disk_usage(Path.home())
    print("Free space now:", show_size(free))
    print("Done.")


if __name__ == "__main__":
    main()
