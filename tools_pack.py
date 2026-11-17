import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path

VERSION = "v1"
FROZEN = getattr(sys, "frozen", False)
EXE_SUFFIX = ".exe" if sys.platform == "win32" else ""
if FROZEN:
    BASE = Path(sys.executable).parent
else:
    BASE = Path(__file__).parent


def tool_command(script):
    if FROZEN:
        exe = script.with_name(script.stem + EXE_SUFFIX)
        return [str(exe)], exe
    return [sys.executable, str(script)], script


DARK = "#1e1e1e"
DARKER = "#161616"
LIGHT = "#e8e8e8"
GREY = "#9a9a9a"
ACCENT = "#00D5FF"
ACCENT_HOVER = "#33E0FF"
ACCENT_TEXT = "#0B1F2A"
INACTIVE = "#2A2A2A"
INACTIVE_HOVER = "#3A3A3A"

TOOLS = [
    (
        "Junk Cleaner",
        BASE / "1-JunkCleaner" / "junk_cleaner.py",
        (
            "Cleans temp and junk files. Shows a preview, "
            "then asks you to type yes before deleting."
        ),
    ),
    (
        "Startup Manager",
        BASE / "2-StartupManager" / "startup_manager.py",
        (
            "Lists apps that start at login. Type numbers "
            "to turn one off, then type yes."
        ),
    ),
    (
        "Duplicate Finder",
        BASE / "3-DuplicateFinder" / "duplicate_finder.py",
        (
            "Finds big files over 100 MB and exact "
            "duplicates. Keeps the first copy."
        ),
    ),
    (
        "Disk Space",
        BASE / "4-DiskSpace" / "disk_space.py",
        (
            "Shows drive space, biggest folders and "
            "files. You can delete big files by number."
        ),
    ),
    (
        "File Organizer",
        BASE / "5-FileOrganizer" / "file_organizer.py",
        (
            "Sorts Downloads and Desktop into folders "
            "by type. Nothing is deleted."
        ),
    ),
    (
        "One-Click",
        BASE / "6-OneClickMaintenance" / "one_click_maintenance.py",
        (
            "Cleans temp files and checks space in "
            "one go, with one yes at the start."
        ),
    ),
    (
        "PC Health",
        BASE / "7-PCHealthReport" / "pc_health_report.py",
        (
            "Plain facts about your computer, saved "
            "to a text file. No score, no fake errors."
        ),
    ),
]


def round_rect(canvas, x1, y1, x2, y2, radius, **kw):
    points = [
        x1 + radius,
        y1,
        x2 - radius,
        y1,
        x2,
        y1,
        x2,
        y1 + radius,
        x2,
        y2 - radius,
        x2,
        y2,
        x2 - radius,
        y2,
        x1 + radius,
        y2,
        x1,
        y2,
        x1,
        y2 - radius,
        x1,
        y1 + radius,
        x1,
        y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kw)


class RoundedButton(tk.Canvas):
    def __init__(
        self,
        parent,
        text,
        command,
        width=200,
        height=42,
        fill=ACCENT,
        hover=ACCENT_HOVER,
        text_fill=ACCENT_TEXT,
        font_size=11,
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=DARK,
            highlightthickness=0,
            bd=0,
        )
        self.command = command
        self.fill = fill
        if fill == INACTIVE:
            self.hover_fill = INACTIVE_HOVER
        else:
            self.hover_fill = hover
        radius = height // 2 - 2
        self.shape = round_rect(
            self, 2, 2, width - 2, height - 2, radius, fill=fill, outline=fill
        )
        self.label = self.create_text(
            width // 2,
            height // 2,
            text=text,
            fill=text_fill,
            font=("Arial", font_size, "bold"),
        )
        self.bind("<Button-1>", self._click)
        self.bind("<Enter>", self._hover)
        self.bind("<Leave>", self._leave)

    def set_fill(self, fill, text_fill=None):
        self.fill = fill
        if fill == INACTIVE:
            self.hover_fill = INACTIVE_HOVER
        else:
            self.hover_fill = ACCENT_HOVER
        self.itemconfig(self.shape, fill=fill, outline=fill)
        if text_fill:
            self.itemconfig(self.label, fill=text_fill)

    def _click(self, event):
        self.command()

    def _hover(self, event):
        self.itemconfig(self.shape, fill=self.hover_fill)

    def _leave(self, event):
        self.itemconfig(self.shape, fill=self.fill)


class ToolTab(tk.Frame):
    def __init__(self, parent, name, script, brief):
        super().__init__(parent, bg=DARK)
        self.script = script
        self.process = None
        self.messages = queue.Queue()

        label = tk.Label(
            self,
            text=brief,
            bg=DARK,
            fg=GREY,
            wraplength=820,
            justify="left",
            font=("Arial", 11),
        )
        label.pack(fill="x", padx=16, pady=(12, 8))

        self.run_button = RoundedButton(
            self, "Run " + name, self.run, width=220, height=48
        )
        self.run_button.pack(padx=16, pady=4, anchor="w")

        self.output = tk.Text(
            self,
            bg=DARKER,
            fg=LIGHT,
            font=("Consolas", 11),
            height=18,
            wrap="word",
            state="disabled",
        )
        self.output.pack(fill="both", expand=True, padx=16, pady=8)

        row = tk.Frame(self, bg=DARK)
        row.pack(fill="x", padx=16, pady=(0, 12))
        self.entry = tk.Entry(
            row,
            bg="#2a2a2a",
            fg=LIGHT,
            font=("Arial", 11),
            insertbackground=LIGHT,
        )
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.send)
        send = RoundedButton(
            row, "Send", lambda: self.send(None), width=100, height=40
        )
        send.pack(side="left", padx=(8, 0))
        self.after(100, self.poll)

    def show(self, text):
        self.output.config(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.config(state="disabled")

    def run(self):
        if self.process is not None:
            return
        command, target = tool_command(self.script)
        if not target.is_file():
            self.show("Tool not found: " + str(target))
            return
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.config(state="disabled")
        self.show("Running " + target.name + "...\n")
        try:
            flags = 0
            if sys.platform == "win32":
                flags = subprocess.CREATE_NO_WINDOW
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=str(self.script.parent),
                creationflags=flags,
            )
        except OSError as error:
            self.show("Could not start it: " + str(error))
            return
        thread = threading.Thread(target=self._read, daemon=True)
        thread.start()
        self.entry.focus_force()

    def _read(self):
        for line in self.process.stdout:
            self.messages.put(line)
        self.messages.put(None)

    def poll(self):
        try:
            while True:
                line = self.messages.get_nowait()
                if line is None:
                    self.process = None
                    self.show("\nDone.\n")
                else:
                    self.show(line)
        except queue.Empty:
            pass
        self.after(100, self.poll)

    def send(self, event):
        if self.process is None:
            return
        text = self.entry.get()
        if not text:
            return
        try:
            self.process.stdin.write(text + "\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError):
            return
        self.show("> " + text + "\n")
        self.entry.delete(0, "end")


def main():
    try:
        root = tk.Tk()
    except tk.TclError:
        print("No screen found. Run it on a computer with a screen.")
        return
    root.title("PurgePad - " + VERSION)
    root.geometry("900x620")
    root.configure(bg=DARK)
    root.overrideredirect(True)
    import os as _os

    try:
        _icon = BASE / "purgepad-icon.png"
        if _icon.exists():
            _photo = tk.PhotoImage(file=str(_icon))
            root.iconphoto(True, _photo)
            root._icon_photo = _photo
    except (tk.TclError, OSError):
        pass

    if _os.environ.get("TOOLS_PACK_NO_ALPHA") != "1":
        try:
            root.attributes("-alpha", 0.9)
        except tk.TclError:
            pass

    top = tk.Frame(root, bg=DARKER, height=38)
    top.pack(fill="x")
    title = tk.Label(
        top,
        text="PurgePad  •  " + VERSION,
        bg=DARKER,
        fg=LIGHT,
        font=("Arial", 12, "bold"),
    )
    title.pack(side="left", padx=16, pady=8)
    close = tk.Button(
        top,
        text="X",
        bg=DARKER,
        fg=LIGHT,
        relief="flat",
        font=("Arial", 12, "bold"),
        command=root.destroy,
    )
    close.pack(side="right", padx=8)

    def start_move(event):
        root._x = event.x_root - root.winfo_x()
        root._y = event.y_root - root.winfo_y()

    def do_move(event):
        root.geometry(f"+{event.x_root - root._x}+{event.y_root - root._y}")

    top.bind("<Button-1>", start_move)
    top.bind("<B1-Motion>", do_move)
    title.bind("<Button-1>", start_move)
    title.bind("<B1-Motion>", do_move)

    tab_bar = tk.Frame(root, bg=DARK)
    tab_bar.pack(fill="x", padx=8, pady=(8, 0))
    body = tk.Frame(root, bg=DARK)
    body.pack(fill="both", expand=True, padx=8, pady=8)

    tabs = []
    tab_buttons = []

    def show_tab(index):
        for i, tab in enumerate(tabs):
            tab.pack_forget()
            if i == index:
                tab.pack(fill="both", expand=True)
                tab_buttons[i].set_fill(ACCENT, ACCENT_TEXT)
            else:
                tab_buttons[i].set_fill(INACTIVE, LIGHT)

    for index, (name, script, brief) in enumerate(TOOLS):
        tab = ToolTab(body, name, script, brief)
        tabs.append(tab)
        button = RoundedButton(
            tab_bar,
            name,
            lambda i=index: show_tab(i),
            width=122,
            height=40,
            fill=INACTIVE,
            text_fill=LIGHT,
            font_size=10,
        )
        button.pack(side="left", padx=2)
        tab_buttons.append(button)
    show_tab(0)

    if "--screenshot-test" in sys.argv:
        root.after(2000, root.destroy)
    root.mainloop()


if __name__ == "__main__":
    main()
