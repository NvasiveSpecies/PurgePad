import os
import subprocess
import sys
import time
from pathlib import Path

import pyautogui

pyautogui.FAILSAFE = False

EXE = sys.argv[1]
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
DUP = os.environ.get("PURGEPAD_DUP_FOLDER", "/tmp/dup_test")
ORG = os.environ.get("PURGEPAD_ORG_FOLDER", "/tmp/org_test")
Y_OFF = 62 if sys.platform == "darwin" else 0


def shot(name):
    path = str(OUT / name)
    if sys.platform == "darwin":
        subprocess.run(["screencapture", "-x", path], check=False)
    elif sys.platform == "win32":
        ps = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "Add-Type -AssemblyName System.Drawing; "
            "$b=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds; "
            "$i=New-Object System.Drawing.Bitmap($b.Width,$b.Height); "
            "$g=[System.Drawing.Graphics]::FromImage($i); "
            "$g.CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size); "
            f"$i.Save('{path}',[System.Drawing.Imaging.ImageFormat]::Png)"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps], check=False
        )
    else:
        try:
            pyautogui.screenshot(path)
        except Exception:
            from mss import mss

            with mss() as s:
                s.shot(output=path)


def click_run():
    pyautogui.click(130, 155 + Y_OFF)
    time.sleep(2)


def answer(text):
    pyautogui.click(400, 585 + Y_OFF)
    time.sleep(0.5)
    pyautogui.click(400, 585 + Y_OFF)
    time.sleep(0.5)
    if sys.platform == "darwin":
        if text:
            subprocess.run(
                ["osascript", "-e",
                 f'tell application "System Events" to keystroke "{text}"'],
                check=False,
            )
        subprocess.run(
            ["osascript", "-e",
             'tell application "System Events" to key code 36'],
            check=False,
        )
    else:
        if text:
            pyautogui.typewrite(text, interval=0.08)
        pyautogui.press("enter")
    time.sleep(2)


proc = subprocess.Popen([EXE])
time.sleep(3)
shot("gui_open.png")
tabs = [
    ("junk", 68, [("no",)]),
    ("startup", 185, []),
    ("duplicate", 310, [(DUP,), ("",), ("no",)]),
    ("diskspace", 435, [(DUP,), ("",)]),
    ("organizer", 560, [("3",), (ORG,), ("yes",)]),
    ("oneclick", 685, [("no",)]),
    ("health", 810, []),
]
def check_gui_alive(step):
    if proc.poll() is not None:
        raise SystemExit(f"FAIL: GUI closed during {step}")


def check_exists(path, step):
    if not Path(path).exists():
        raise SystemExit(f"FAIL: {step}: missing {path}")
    print("ok:", step, path, flush=True)


def check_missing(path, step):
    if Path(path).exists():
        raise SystemExit(f"FAIL: {step}: still there {path}")
    print("ok:", step, "gone", path, flush=True)


for name, x, answers in tabs:
    pyautogui.click(x, 65 + Y_OFF)
    time.sleep(1)
    click_run()
    for (text,) in answers:
        answer(text)
    time.sleep(1)
    shot(f"gui_{name}.png")
    check_gui_alive(name)
    if name == "duplicate":
        check_exists(Path(DUP) / "a.txt", "duplicate keeps a")
        check_exists(Path(DUP) / "b.txt", "duplicate keeps b")
    if name == "diskspace":
        check_exists(Path(DUP) / "a.txt", "diskspace keeps a")
        check_exists(Path(DUP) / "b.txt", "diskspace keeps b")
    if name == "organizer":
        check_exists(Path(ORG) / "Images" / "photo.jpg", "organizer moved photo")
        check_exists(Path(ORG) / "Documents" / "note.txt", "organizer moved note")
        check_missing(Path(ORG) / "photo.jpg", "organizer moved photo")
        check_missing(Path(ORG) / "note.txt", "organizer moved note")
    print("done tab", name, flush=True)
check_gui_alive("all tabs")
proc.terminate()
print("ALL TABS DONE - GUI OPERATED OK")
