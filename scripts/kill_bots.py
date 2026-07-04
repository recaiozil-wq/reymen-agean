"""Bot process'lerini bulup oldur."""

import subprocess, sys

# Tum python process'lerini listele
r = subprocess.run(
    ["tasklist", "/fi", "imagename eq python.exe", "/fo", "csv", "/v"],
    capture_output=True,
    text=True,
    timeout=10,
    creationflags=subprocess.CREATE_NO_WINDOW,
)

oldurulen = 0
for line in r.stdout.splitlines():
    if "telegram_bot.py" in line or "bot_supervisor" in line:
        parts = line.split(",")
        if len(parts) >= 2:
            pid = parts[1].strip().strip('"')
            if pid.isdigit():
                subprocess.run(
                    ["taskkill", "/f", "/pid", pid],
                    capture_output=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                print(f"Olduruldu: PID {pid}")
                oldurulen += 1

print(f"Toplam oldurulen: {oldurulen}")
