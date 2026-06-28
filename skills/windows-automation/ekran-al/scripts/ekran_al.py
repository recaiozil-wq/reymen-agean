import subprocess
from pathlib import Path
from datetime import datetime

# Çıktı klasörü
OUT_DIR = Path(r'C:\Users\marko\Desktop\ekran_gorselleri')
OUT_DIR.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
out_path = OUT_DIR / f'ekran_{timestamp}.png'

# Win+Shift+S tarafından alınan geçici görüntüyü bul
clipboard_dir = Path(r'C:\Users\marko\AppData\Local\Temp\MediaCache')
latest_img = max(clipboard_dir.glob('*.png'), key=lambda p: p.stat().st_mtime) if any(clipboard_dir.glob('*.png')) else None

if latest_img:
    out_path.write_bytes(latest_img.read_bytes())
    print(f'OK: {out_path}')
else:
    # Alternatif: PowerShell ile PrintScreen + kaydetme denemesi
    ps = f'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("{{PRTSC}}"); Start-Sleep -Milliseconds 500; $c = [System.Windows.Forms.Clipboard]::GetImage(); $c.Save("{out_path}")'
    r = subprocess.run(['powershell', '-Command', ps], capture_output=True, text=True)
    if out_path.exists():
        print(f'OK: {out_path}')
    else:
        print('HATA: Görüntü alınamadı')
