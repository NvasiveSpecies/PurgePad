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
