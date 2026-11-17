import hashlib
from pathlib import Path

LARGE_MB = 100
CHUNK = 1024 * 1024


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
    for path in folder.rglob("*"):
        if not path.is_file():
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        files.append((path, size))
    return files


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

    files = scan(folder)
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
        print("  ", show_size(size), "each:")
        for path in paths:
            print("    ", path)
        print("     Keep:", paths[0])
        to_delete.extend(paths[1:])
    print()
    print("Extra copies that could be deleted:", len(to_delete))
    print()

    answer = input("Delete the extra copies? Type yes to go: ")
    if answer.strip().lower() != "yes":
        print("Stopped. Nothing was deleted.")
        return

    freed = 0
    done = 0
    for path in to_delete:
        try:
            freed += path.stat().st_size
            path.unlink()
            done += 1
        except OSError:
            print("Could not delete:", path)
    print("Deleted:", done, "files, freed", show_size(freed))
    print("Done.")


if __name__ == "__main__":
    main()
