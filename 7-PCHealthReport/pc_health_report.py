import os
import platform
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path


def show_size(size):
    if size >= 1024 * 1024 * 1024:
        return str(round(size / 1024**3, 2)) + " GB"
    if size >= 1024 * 1024:
        return str(round(size / 1024**2, 1)) + " MB"
    if size >= 1024:
        return str(round(size / 1024, 1)) + " KB"
    return str(size) + " B"


def memory_info():
    path = Path("/proc/meminfo")
    if not path.is_file():
        return "Memory: not shown on this system"
    total = 0
    free = 0
    try:
        for line in path.read_text().splitlines():
            if line.startswith("MemTotal:"):
                total = int(line.split()[1]) * 1024
            if line.startswith("MemAvailable:"):
                free = int(line.split()[1]) * 1024
    except (OSError, ValueError):
        return "Memory: could not be read"
    if not total:
        return "Memory: could not be read"
    return "Memory total: " + show_size(total) + ", free: " + show_size(free)


def temp_info():
    folders = [
        Path(tempfile.gettempdir()),
        Path("/tmp"),
        Path.home() / ".cache",
    ]
    count = 0
    size = 0
    seen = []
    for folder in folders:
        if folder.is_dir() and folder not in seen:
            seen.append(folder)
            for path in folder.rglob("*"):
                if path.is_file():
                    try:
                        count += 1
                        size += path.stat().st_size
                    except OSError:
                        continue
    return count, size


def startup_count():
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
    return 0


def count_files(folder):
    if not folder.is_dir():
        return 0
    return len([p for p in folder.iterdir() if p.is_file()])


def main():
    lines = []
    lines.append("PC Health Report")
    lines.append("Date: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    lines.append("")
    lines.append("System: " + platform.system() + " " + platform.release())
    lines.append("Computer: " + platform.machine())
    lines.append("Processor: " + (platform.processor() or "not shown"))
    lines.append("CPU cores: " + str(os.cpu_count()))
    lines.append("Python: " + sys.version.split()[0])
    try:
        load = os.getloadavg()
        lines.append(
            "Load average: "
            + str(round(load[0], 2))
            + ", "
            + str(round(load[1], 2))
            + ", "
            + str(round(load[2], 2))
        )
    except (AttributeError, OSError):
        lines.append("Load average: not shown")
    lines.append(memory_info())
    lines.append("")

    total, used, free = shutil.disk_usage(Path.home())
    lines.append("Drive total: " + show_size(total))
    lines.append(
        "Drive used: "
        + show_size(used)
        + " - "
        + str(round(used / total * 100, 1))
        + "%"
    )
    lines.append(
        "Drive free: "
        + show_size(free)
        + " - "
        + str(round(free / total * 100, 1))
        + "%"
    )
    lines.append("")

    count, size = temp_info()
    lines.append("Temp files: " + str(count) + " - " + show_size(size))
    lines.append("Startup apps: " + str(startup_count()))
    lines.append(
        "Downloads files: " + str(count_files(Path.home() / "Downloads"))
    )
    lines.append("Desktop files: " + str(count_files(Path.home() / "Desktop")))
    lines.append("")
    lines.append("No score, no warnings, no fake errors.")
    lines.append("Done.")

    text = "\n".join(lines)
    print(text)
    out = Path(__file__).parent / "pc_health_report.txt"
    out.write_text(text + "\n", encoding="utf-8")
    print()
    print("Saved to:", out)


if __name__ == "__main__":
    main()
