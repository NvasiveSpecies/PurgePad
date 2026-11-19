import os
import platform
from pathlib import Path


class StartupItem:
    def __init__(self, name, kind, path, detail=""):
        self.name = name
        self.kind = kind
        self.path = path
        self.detail = detail

    def show(self, number):
        print(number, "-", self.name)
        print("   ", self.kind, ":", self.path)
        if self.detail:
            print("   ", self.detail)


def read_desktop_file(path):
    name = path.stem
    command = ""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return name, command
    for line in text.splitlines():
        if line.startswith("Name="):
            name = line[5:].strip()
        if line.startswith("Exec="):
            command = line[5:].strip()
    return name, command


def get_linux_items():
    items = []
    folder = Path.home() / ".config" / "autostart"
    if not folder.is_dir():
        return items
    for path in sorted(folder.glob("*.desktop")):
        name, command = read_desktop_file(path)
        items.append(StartupItem(name, "autostart", path, command))
    for path in sorted(folder.glob("*.desktop.disabled")):
        name = path.name.replace(".desktop.disabled", "")
        items.append(StartupItem(name + " (off)", "autostart", path, ""))
    return items


def get_mac_items():
    items = []
    folder = Path.home() / "Library" / "LaunchAgents"
    if not folder.is_dir():
        return items
    for path in sorted(folder.glob("*.plist")):
        items.append(StartupItem(path.stem, "LaunchAgent", path, ""))
    return items


def get_windows_items():
    items = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        folder = Path(appdata) / "Microsoft" / "Windows"
        folder = folder / "Start Menu" / "Programs"
        folder = folder / "Startup"
        if folder.is_dir():
            for path in sorted(folder.iterdir()):
                items.append(
                    StartupItem(path.name, "Startup folder", path, "")
                )
    try:
        import winreg
    except ImportError:
        return items
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
        )
    except OSError:
        return items
    index = 0
    while True:
        try:
            name, value, _kind = winreg.EnumValue(key, index)
        except OSError:
            break
        items.append(StartupItem(name, "Run key", "HKCU Run", value))
        index += 1
    winreg.CloseKey(key)
    return items


def get_items():
    system = platform.system()
    if system == "Windows":
        return get_windows_items()
    if system == "Darwin":
        return get_mac_items()
    return get_linux_items()


def disable_item(item):
    if item.kind == "Run key":
        try:
            import winreg
        except ImportError:
            return False
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ | winreg.KEY_SET_VALUE,
            )
            value, kind = winreg.QueryValueEx(key, item.name)
            backup = winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\PurgePad\StartupBackup",
            )
            winreg.SetValueEx(backup, item.name, 0, kind, value)
            winreg.CloseKey(backup)
            winreg.DeleteValue(key, item.name)
            winreg.CloseKey(key)
            return True
        except OSError:
            return False
    try:
        path = Path(item.path)
        if not path.exists():
            return False
        if path.suffix == ".disabled":
            return False
        new_path = path.with_suffix(path.suffix + ".disabled")
        if str(path).endswith(".desktop"):
            new_path = Path(str(path) + ".disabled")
        if new_path.exists():
            return False
        path.rename(new_path)
        return True
    except (OSError, PermissionError):
        return False


def main():
    print("Startup Manager")
    print("System:", platform.system())
    print()

    items = get_items()
    if not items:
        print("No startup items found.")
        print("That is normal on a clean system.")
        return

    print("These apps start when you log in:")
    print()
    for number, item in enumerate(items, 1):
        item.show(number)
    print()
    print("Turning one off does not delete the app.")
    print("It only stops it starting by itself.")
    print()

    answer = input(
        "Type numbers to turn off, like 1,3, or press Enter to stop: "
    )
    if not answer.strip():
        print("Stopped. Nothing was changed.")
        return

    picks = []
    for part in answer.split(","):
        part = part.strip()
        if part.isdigit():
            number = int(part)
            if 1 <= number <= len(items):
                picks.append(items[number - 1])

    if not picks:
        print("No valid numbers. Nothing was changed.")
        return

    print()
    print("You picked:")
    for item in picks:
        print("  ", item.name)
    print()

    confirm = input("Turn these off? Type yes to go: ")
    if confirm.strip().lower() != "yes":
        print("Stopped. Nothing was changed.")
        return

    for item in picks:
        if disable_item(item):
            print("Turned off:", item.name)
        else:
            print("Could not turn off:", item.name)
    print("Done.")


if __name__ == "__main__":
    main()
