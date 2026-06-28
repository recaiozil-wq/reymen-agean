"""
Mod 1: learn_position.py           → bekle, tıkla, temp'e kaydet, koordinatı yaz
Mod 2: learn_position.py ad        → bekle, tıkla, direkt ada kaydet
Mod 3: learn_position.py --rename ad → temp'i yeniden adlandır
Mod 4: learn_position.py --list    → kayıtlı konumları listele
"""
import sys
import json
import os
import time
import ctypes

POSITIONS_FILE = r"C:\Users\marko\AppData\Local\ReYMeN\skills\vscode-agent-control\positions.json"

def load():
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save(data):
    with open(POSITIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_mouse_pos():
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def wait_for_click(seconds=6):
    VK_LBUTTON = 0x01
    user32 = ctypes.windll.user32
    deadline = time.time() + seconds
    prev = user32.GetAsyncKeyState(VK_LBUTTON)
    while time.time() < deadline:
        state = user32.GetAsyncKeyState(VK_LBUTTON)
        if state != prev and (state & 0x8000):
            return get_mouse_pos()
        prev = state
        time.sleep(0.05)
    return None

if __name__ == "__main__":
    args = sys.argv[1:]

    # --list: kayıtlı konumları göster
    if "--list" in args or not args:
        data = load()
        if data:
            for name, coords in data.items():
                if name != "_temp":
                    print(f"  {name}: ({coords['x']}, {coords['y']})")
        else:
            print("Henüz kayıtlı konum yok.")
        sys.exit(0)

    # --rename <ad>: temp konumu yeniden adlandır
    if "--rename" in args:
        idx = args.index("--rename")
        new_name = " ".join(args[idx+1:])
        data = load()
        if "_temp" not in data:
            print("ERROR: Önce konum kaydedin.")
            sys.exit(1)
        data[new_name] = data.pop("_temp")
        save(data)
        print(f"SAVED: '{new_name}' = ({data[new_name]['x']}, {data[new_name]['y']})")
        sys.exit(0)

    # Normal mod: tıklamayı bekle
    name = " ".join(args) if args else "_temp"
    print(f"HAZIR: 6 saniye içinde tıklayın...")

    pos = wait_for_click(6)
    if pos:
        x, y = pos
        data = load()
        data[name] = {"x": x, "y": y}
        save(data)
        if name == "_temp":
            print(f"CLICKED: ({x}, {y}) — Şimdi adını yazın.")
        else:
            print(f"SAVED: '{name}' = ({x}, {y})")
    else:
        print("TIMEOUT: Tıklama algılanamadı.")
        sys.exit(1)
