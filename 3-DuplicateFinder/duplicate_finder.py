import hashlib
import os
import platform
from pathlib import Path

try:
    import fcntl
except ImportError:
    fcntl = None

LARGE_MB = 100
CHUNK = 1024 * 1024


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


def is_in_use(path, open_set):
    try:
        info = path.stat()
    except OSError:
        return False
    if (info.st_dev, info.st_ino) in open_set:
        return True
    return is_locked(path)


def show_size(size):
    return str(round(size / 1024 / 1024, 1)) + " MB"


def file_hash(path):
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as handle:
            while True:
                chunk = handle.read(CHUNK)
                if not chunk:
                    break
                hasher.update(chunk)
    except OSError:
        return ""
    return hasher.hexdigest()


def scan(folder):
    files = []
    link_targets = set()
    for path in folder.rglob("*"):
        if path.is_symlink():
            try:
                link_targets.add(path.resolve())
            except OSError:
                pass
            continue
        if not path.is_file():
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        files.append((path, size))
    return files, link_targets


def main():
    print("Duplicate and Large-File Finder")
    print()

    text = input("Folder to check? Press Enter for your home folder: ")
    if text.strip():
        folder = Path(text.strip()).expanduser()
    else:
        folder = Path.home()
    if not folder.is_dir():
        print("That folder does not exist.")
        return

    print("Checking:", folder)
    print("This can take a minute on big folders.")
    print()

    files, link_targets = scan(folder)
    if not files:
        print("No files found.")
        return

    large = []
    for path, size in files:
        if size >= LARGE_MB * 1024 * 1024:
            large.append((path, size))
    large.sort(key=lambda item: item[1], reverse=True)

    print("Big files over", LARGE_MB, "MB:")
    if not large:
        print("  None found.")
    for path, size in large[:20]:
        print("  ", show_size(size), "-", path)
    print()

    by_size = {}
    for path, size in files:
        by_size.setdefault(size, []).append(path)

    groups = []
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        by_hash = {}
        for path in paths:
            digest = file_hash(path)
            if digest:
                by_hash.setdefault(digest, []).append(path)
        for paths2 in by_hash.values():
            if len(paths2) > 1:
                groups.append((size, paths2))

    print("Duplicate files:")
    if not groups:
        print("  None found.")
        print("Done.")
        return

    to_delete = []
    for size, paths in groups:
        paths.sort(key=lambda p: p.resolve() not in link_targets)
        print("  ", show_size(size), "each:")
        for number, path in enumerate(paths, 1):
            print("    ", number, "-", path)
        keep = 0
        pick = input(
            "Which one stays? Type the number, or press Enter "
            "to keep the first: "
        )
        if pick.strip().isdigit():
            number = int(pick.strip())
            if 1 <= number <= len(paths):
                keep = number - 1
        print("     Keep:", paths[keep])
        for index, path in enumerate(paths):
            if index == keep:
                continue
            try:
                if path.resolve() in link_targets:
                    continue
            except OSError:
                pass
            to_delete.append(path)
    print()
    print("Extra copies that could be deleted:", len(to_delete))
    print()

    answer = input("Delete the extra copies? Type yes to go: ")
    if answer.strip().lower() != "yes":
        print("Stopped. Nothing was deleted.")
        return

    open_set = open_inodes()
    freed = 0
    done = 0
    skipped = 0
    for path in to_delete:
        if is_in_use(path, open_set):
            skipped += 1
            print("Skipped (in use):", path)
            continue
        try:
            freed += path.stat().st_size
            path.unlink()
            done += 1
        except OSError:
            print("Could not delete:", path)
    if skipped:
        print("Skipped", skipped, "files that were in use.")
    print("Deleted:", done, "files, freed", show_size(freed))
    print("Done.")


if __name__ == "__main__":
    main()
