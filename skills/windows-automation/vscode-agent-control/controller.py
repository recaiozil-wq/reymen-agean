"""
VS Code Claude Agent Terminal Controller
positions.json'daki kayıtlı konumları kullanarak yazar.
"""
import sys
import time
import json
import os
import ctypes
import subprocess
import pyautogui
from datetime import datetime

POSITIONS_FILE = r"C:\Users\marko\AppData\Local\ReYMeN\skills\vscode-agent-control\positions.json"
SCREENSHOT_DIR = r"C:\Users\marko\AppData\Local\ReYMeN\screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

user32 = ctypes.windll.user32

def load_positions():
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}

def find_window(fragment):
    found = []
    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(hwnd, buf, 512)
            if fragment.lower() in buf.value.lower():
                found.append(hwnd)
        return True
    user32.EnumWindows(cb, 0)
    return found[0] if found else None

def maximize_focus(hwnd):
    user32.ShowWindow(hwnd, 3)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.8)

def screenshot(label="snap"):
    ts = datetime.now().strftime("%H%M%S")
    path = os.path.join(SCREENSHOT_DIR, f"{label}_{ts}.png")
    pyautogui.screenshot(path)
    return path

def run(message: str, target: str = "claude terminal"):
    positions = load_positions()

    # VS Code bul ve maximize et
    hwnd = find_window("Visual Studio Code")
    if not hwnd:
        subprocess.Popen(["code"])
        time.sleep(4)
        hwnd = find_window("Visual Studio Code")
    if not hwnd:
        print("ERROR: VS Code acılamadı")
        sys.exit(1)

    maximize_focus(hwnd)

    # Kayıtlı konuma tıkla
    if target in positions:
        pos = positions[target]
        x, y = pos["x"], pos["y"]
        print(f"Kayıtlı konum kullanılıyor: {target} = ({x},{y})")
        pyautogui.click(x, y)
        time.sleep(0.5)
    else:
        # Fallback: pencere boyutuna göre tahmin
        class RECT(ctypes.Structure):
            _fields_ = [("left",ctypes.c_long),("top",ctypes.c_long),
                        ("right",ctypes.c_long),("bottom",ctypes.c_long)]
        r = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(r))
        w = r.right - r.left
        h = r.bottom - r.top
        x = r.left + int(w * 0.87)
        y = r.top  + int(h * 0.96)
        print(f"Tahmin edilen konum: ({x},{y}) - 'kaydet: {target}' ile öğretin")
        pyautogui.click(x, y)
        time.sleep(0.5)

    # Clipboard üzerinden yapıştır (Türkçe karakter desteği)
    subprocess.run(
        ["powershell", "-command", f"Set-Clipboard -Value @'\n{message}\n'@"],
        capture_output=True
    )
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.3)
    pyautogui.press("enter")
    time.sleep(0.5)

    after = screenshot("after")
    print(f"after: {after}")
    print("SUCCESS")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: controller.py <mesaj> [--target <konum_adı>]")
        sys.exit(1)

    args = sys.argv[1:]
    target = "claude terminal"
    if "--target" in args:
        idx = args.index("--target")
        target = args[idx + 1]
        args = args[:idx] + args[idx+2:]

    run(" ".join(args), target)
