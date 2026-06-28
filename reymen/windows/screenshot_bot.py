"""ReYMeN bot için ekran görüntüsü scripti.
Python 3.14 (sistem Python'u) ile çalışır, mss kütüphanesini kullanır.
Çağırma: python3.14 screenshot_bot.py
Çıktı: ekran.png -> CWD'ye kaydeder
"""
import subprocess, sys, os

SCRIPT = r"""
import mss
with mss.mss() as sct:
    monitor = sct.monitors[1]  # primary monitor
    sct.shot(output="ekran.png")
print("OK: ekran.png kaydedildi")
"""

# Python 3.14 yolunu dene
for py in [
    r"C:\Users\marko\AppData\Local\Python\PythonCore-3.14-64\python.exe",
    r"C:\Users\marko\AppData\Local\Programs\Python\Python314\python.exe",
]:
    if os.path.exists(py):
        r = subprocess.run([py, "-c", SCRIPT], capture_output=True, text=True, timeout=30)
        print(r.stdout)
        if r.stderr:
            print("STDERR:", r.stderr[:500])
        sys.exit(r.returncode)

print("FAIL: Python 3.14 not found")
sys.exit(1)
