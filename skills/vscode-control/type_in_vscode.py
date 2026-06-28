import sys
import time
import ctypes
import subprocess
import pyautogui

user32 = ctypes.windll.user32

def find_vscode_hwnd():
    result = []
    def cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(hwnd, buf, 256)
            title = buf.value
            if "Visual Studio Code" in title or ("Code" in title and ".py" in title):
                result.append(hwnd)
        return True
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    user32.EnumWindows(EnumWindowsProc(cb), 0)
    return result[0] if result else None

def focus_vscode():
    hwnd = find_vscode_hwnd()
    if not hwnd:
        subprocess.Popen(["code"])
        time.sleep(3)
        hwnd = find_vscode_hwnd()
    if hwnd:
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        return True
    return False

def type_text(text):
    pyautogui.PAUSE = 0.04
    pyautogui.typewrite(text, interval=0.04)

def press_keys(keys):
    parts = keys.lower().split("+")
    if len(parts) > 1:
        pyautogui.hotkey(*parts)
    else:
        pyautogui.press(keys)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: type_in_vscode.py [type|press|open] <text_or_keys_or_path>")
        sys.exit(1)

    action = sys.argv[1]
    arg = " ".join(sys.argv[2:])

    if action == "open":
        subprocess.Popen(["code", arg])
        print(f"Opened: {arg}")
        sys.exit(0)

    if not focus_vscode():
        print("VS Code penceresi bulunamadi")
        sys.exit(1)

    if action == "type":
        type_text(arg)
        print(f"Yazildi: {arg}")
    elif action == "press":
        press_keys(arg)
        print(f"Tus basildi: {arg}")
    else:
        print(f"Bilinmeyen eylem: {action}")
        sys.exit(1)
