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
        pyautogui.screenshot(path)


def click_run():
    pyautogui.click(130, 155)
    time.sleep(2)


def answer(text):
    pyautogui.click(400, 585)
    if text:
        pyautogui.typewrite(text, interval=0.04)
    pyautogui.press("enter")
    time.sleep(2)


proc = subprocess.Popen([EXE])
time.sleep(3)
shot("gui_open.png")
tabs = [
    ("junk", 68, [("no",)]),
    ("startup", 185, []),
    ("duplicate", 310, [(DUP,), ("no",)]),
    ("diskspace", 435, [(DUP,), ("",)]),
    ("organizer", 560, [("3",), (ORG,), ("yes",)]),
    ("oneclick", 685, [("no",)]),
    ("health", 810, []),
]
for name, x, answers in tabs:
    pyautogui.click(x, 65)
    time.sleep(1)
    click_run()
    for (text,) in answers:
        answer(text)
    time.sleep(1)
    shot(f"gui_{name}.png")
    print("done tab", name, flush=True)
proc.terminate()
print("ALL TABS DONE")
