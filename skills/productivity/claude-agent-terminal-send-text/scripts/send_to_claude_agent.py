"""
VS Code Claude Agent chat input'una metin gonderme scripti.

Kullanim:
  1. METIN ve X,Y degiskenlerini guncelle (write_file ile)
  2. Dogrudan calistir:
     "C:\\Users\\marko\\AppData\\Local\\Python\\PythonCore-3.14-64\\python.exe" script.py

YAZMA MODLARI:
  - HIZLI: interval=0.01 (normal, bot algilamasi riski var)
  - NORMAL: interval=0.05 (guvenli, varsayilan)
  - DOGAL: char-by-char + random.uniform(0.2, 0.4) (bot algilamasini atlatir)
    Yukaridaki icin NATURAL=True yap ve METIN'i ayarla

UYARI:
  - ctrl+a kullanma - tum VS Code icerigini secer
  - Script calisirken fareye dokunma - odagi kaybeder
"""
import pyautogui, time, random

pyautogui.FAILSAFE = False

# === GONDERILECEK METIN ===
METIN = 'Wifi bagli cihazlar ip ve mac adresleri nelerdir'
# =============================

# === YAZMA MODU ===
NATURAL = True   # True = bot algilamasini atlat (yavas), False = normal hiz
NATURAL_MIN = 0.2  # dogal modda min gecikme (saniye)
NATURAL_MAX = 0.4  # dogal modda max gecikme (saniye)
NORMAL_INTERVAL = 0.05  # normal modda harf arasi (saniye)
# ===================

# === KOORDINAT ===
X, Y = 606, 802
# =================

# Tikla ve bekle
pyautogui.click(X, Y)
time.sleep(1.5)

if NATURAL:
    # Dogal yazma - her harf arasi rastgele gecikme (bot algilamasini atlatir)
    for char in METIN:
        pyautogui.write(char, interval=0)
        time.sleep(random.uniform(NATURAL_MIN, NATURAL_MAX))
else:
    # Normal hizli yazma
    pyautogui.write(METIN, interval=NORMAL_INTERVAL)

time.sleep(1.5)
pyautogui.press('enter')

mode = "DOGAL" if NATURAL else f"NORMAL (interval={NORMAL_INTERVAL})"
print(f"OK: ({X},{Y}) - '{METIN}' gonderildi [{mode}]")
