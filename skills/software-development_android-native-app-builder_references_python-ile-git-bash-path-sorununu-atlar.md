---
name: software-development_android-native-app-builder_references_python-ile-git-bash-path-sorununu-atlar
description: Python ile (Git Bash path sorununu atlar)
title: "Software Development Android Native App Builder References Python Ile Git Bash Path Sorununu Atlar"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Python ile (Git Bash path sorununu atlar) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Python ile (Git Bash path sorununu atlar)
import subprocess
adb = r'C:\\...\\platform-tools\\adb.exe'
subprocess.run([adb, 'exec-out', 'screencap', '-p'], stdout=open('screenshot.png', 'wb'))
```

### OCR ile Ekran Doğrulama
Her ADB işleminden sonra ekran görüntüsü alıp OCR ile uygulama durumunu doğrula:

```python
import pytesseract, cv2
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

img = cv2.imread('emulator_screen.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
text = pytesseract.image_to_string(gray, lang='eng+tur')
print(text)  # "Dinleniyor...", "Durduruldu", "Hazır" gibi durum metinlerini göster
```

**Önemli:** Tesseract yolu her sistemde aynı olmayabilir. `which tesseract` veya `C:\Program Files\Tesseract-OCR\tesseract.exe` ile kontrol et. Python'dan kullanırken `pytesseract.tesseract_cmd`'i mutlaka set et.

**OCR ile doğrulanabilen durumlar:**
- Uygulama açıldı mı? → "Canlı Transkript" başlığını ara
- İzin dialog'u mu? → "Allow", "While using the app" metinlerini ara
- Transkripsiyon başladı mı? → "Dinleniyor..." metnini ara
- Transkripsiyon durdu mu? → "Durduruldu" metnini ara

### Logcat Debug
```bash
