---
skill_id: 95f21b2131d2
usage_count: 1
last_used: 2026-06-16
---
# Aktif Konu Tespiti — Referans

## Problem
Kullanıcı "araştırma yap" dediğinde ReYMeN takılı değilse aktif konu bilinmiyor. Takildi.txt yok. Ekranı okuyarak durumu anlamak gerekiyor.

## Çözüm Akışı

### Adım 1: Ekran Görüntüsü Al
```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen((New-Object System.Drawing.Point(0,0)), (New-Object System.Drawing.Point(0,0)), $bmp.Size)
$bmp.Save('C:\Users\marko\Desktop\screen_debug.png', [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()
Write-Output 'OK'
"
```

### Adım 2: JPEG'e Çevir (PIL ile)
PIL RGBA'dan JPEG'e yazamaz — önce RGB'ye convert et:
```python
from PIL import Image
img = Image.open('C:/Users/marko/Desktop/screen_debug.png')
if img.mode == 'RGBA':
    img = img.convert('RGB')
img = img.resize((1280, 720), Image.LANCZOS)
img.save('C:/Users/marko/Desktop/screen_small.jpg', 'JPEG', quality=60)
```

### Adım 3: vision_analyze ile Oku
```python
vision_analyze(image_url='C:/Users/marko/Desktop/screen_small.jpg', question='...')
```

### Adım 4: Ekran Yorumla
Ekranda tipik olarak:
- **Sol taraf:** PowerShell / ReYMeN terminali — MAC analizi, kod çıktısı, hata mesajları
- **Sağ taraf:** Kali Linux VM (VirtualBox) — Wi-Fi taraması, araç kurulumları
- **Alt kısım:** ReYMeN agent durumu (model adı, session süresi)

### Adım 5: Kullanıcıya Raporla
Format:
```
ReYMeN şu an <konu> üzerinde çalışıyor.
Blokaj: <sorun>
Çözüm için: <yapılacak adım>
```

## Session Örneği (2026-06-07)
- **Konu:** Samsung Galaxy S22 Plus MAC/Wi-Fi analizi (SSID "S 22 PLAS")
- **Blokaj:** Kali VM'de `iw` ve `wireless-tools` paketleri eksik → Wi-Fi taraması yapılamıyor
- **Çözüm:** `sudo apt install -y iw wireless-tools` çalıştırıldı, başarılı
- **Not:** `iw` zaten kuruluydu, `wireless-tools` eksikti
- **Model:** DeepSeek (deepseek-chat) — vision desteklemez, vision_analyze fallback kullanır
