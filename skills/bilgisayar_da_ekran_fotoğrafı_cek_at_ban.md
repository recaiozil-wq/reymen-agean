---
name: Bilgisayar da ekran fotoğrafı cek at ban
description: Tamamlanamadi: tur asimi
created: 2026-06-18
usage_count: 1
last_used: 2026-06-18
---

# Bilgisayar da ekran fotoğrafı cek at ban

Tamamlanamadi: tur asimi

## Adimlar

PYTHON_CALISTIR: "import pyautogui; import sys; print('pyautogui version:', pyautogui.__version__)"
PYTHON_CALISTIR: "from PIL import ImageGrab; import sys; print('PIL ImageGrab mevcut'); im = ImageGrab.grab(); im.save('ekran.png'); print('Ekran goruntusu ekran.png olarak kaydedildi')"
KOMUT_CALISTIR: "powershell -Command \"Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; $bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height; $graphics = [System.Drawing.Graphics]::FromImage($bitmap); $graphics.CopyFromScreen($screen.X, $screen.Y, 0, 0, $screen.Size); $bitmap.Save('ekran.png', [System.Drawing.Imaging.ImageFormat]::Png); $graphics.Dispose(); $bitmap.Dispose(); Write-Output 'Ekran goruntusu alindi: ekran.png'\""
KOMUT_CALISTIR: "powershell -Command \"Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; $bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height; $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($bounds.X, $bounds.Y, 0, 0, $bounds.Size); $bmp.Save('ekran.png', [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose(); Write-Host 'Ekran goruntusu alindi: ekran.png'\""
DOSYA_YAZ: "screenshot.ps1", "Add-Type -AssemblyName System.Windows.Forms`nAdd-Type -AssemblyName System.Drawing`n`$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds`n`$bmp = New-Object System.Drawing.Bitmap `$bounds.Width, `$bounds.Height`n`$g = [System.Drawing.Graphics]::FromImage(`$bmp)`n`$g.CopyFromScreen(`$bounds.X, `$bounds.Y, 0, 0, `$bounds.Size)`n`$bmp.Save('ekran.png', [System.Drawing.Imaging.ImageFormat]::Png)`n`$g.Dispose()`n`$bmp.Dispose()`nWrite-Host 'Ekran goruntusu alindi: ekran.png'"
PYTHON_CALISTIR: "import base64; cmd = \"Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; $bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height; $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($bounds.X, $bounds.Y, 0, 0, $bounds.Size); $bmp.Save('ekran.png', [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose(); Write-Host 'OK'\"; print(base64.b64encode(cmd.encode('utf-16le')).decode())"
PYTHON_CALISTIR: "import base64; cmd = 'Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; $bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height; $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($bounds.X, $bounds.Y, 0, 0, $bounds.Size); $bmp.Save(\"ekran.png\", [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose(); Write-Host \"OK\"'; encoded = base64.b64encode(cmd.encode('utf-16le')).decode(); print(encoded)"
