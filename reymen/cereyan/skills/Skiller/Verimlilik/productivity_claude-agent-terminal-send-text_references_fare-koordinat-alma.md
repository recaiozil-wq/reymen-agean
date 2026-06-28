
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Productivity_Claude Agent Terminal Send Text_References_Fare Koordinat Alma |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Fare Koordinat Alma — VS Code Terminalleri

## Yöntem: time.sleep() + GetCursorPos

Script: C:\Users\marko\AppData\Local\hermes\scripts\get_click_coord.py

```python
import ctypes, time
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
user32 = ctypes.windll.user32
cursor = POINT()
time.sleep(3)  # 3sn — kullanici hazir
user32.GetCursorPos(ctypes.byref(cursor))
print(f"Koordinat: ({cursor.x}, {cursor.y})")
```

Cagirma:
"C:\Users\marko\AppData\Local\Python\PythonCore-3.14-64\python.exe" "C:\Users\marko\AppData\Local\hermes\scripts\get_click_coord.py"

## Onemli Uyarilar

- Bu yontem kullanicinin tiklamasini beklemez. time.sleep() bittiginde fare neredeyse onu okur.
- Sleep suresi 3sn idealdir. 10sn cok uzun — kullanici unutur, fare kayar.
- Kullanici tiklamadiysa: eski fare pozisyonunu dondurur -> yanlis koordinat
- Cozum: her okumadan sonra kullaniciya dogrulat "Bu dogru yer mi?"
- Kullanici "Hayir", "Hata", "Yanlis" derse -> script'i hemen tekrar calistir, sorgulama yapma
- GetAsyncKeyState(0x01) PowerShell/terminal altinda CALISMAZ — hic kullanma
- ctypes.wintypes.POINT() calismaz -> kendi POINT(ctypes.Structure) class'ini tanimla

## UYARI: Koordinat Her Oturumda Degisir

Her VS Code acilisinda koordinat sifirlanir. Asla bir onceki oturumun koordinatini kullanma. Her seferinde:
1. Kullaniciya "Fareyi hedefe gotur ve tikla, 3sn" mesaji gonder
2. Koordinat oku (3sn sleep)
3. Kullaniciya dogrulat

## ⚠ OTOM VS CODE ODAK SORUNU VE COZUMU (03.06.2026)

Bu oturumda 7 farkli koordinat alindi ve HICBIRI dogru calismadi:
- (890, 133) -> "chat bokumu aciliyor" (VS Code chat butonu)
- (606, 802) -> metin karisik yazildi, yarisi chat yarisi terminal
- (646, 773) -> yine basarisiz
- (1113, 166) -> calisti ama sadece bir kez

Bu durumun en buyuk sebebi: pyautogui.click() ile tiklanan noktaya VS Code'un
oda degistirme mekanizmasi mudahale ediyor. Click calisiyor ama write() calisana
kadar VS Code odagi baska bir UI elementine kaydiriyor.

COZUM: Artik sadece koordinat degistirme ile ugrasma. Bunun yerine:
1. ZoomIt (veya benzeri bir screen-annotation tool) kullanarak terminalin
   ekrandaki tam konumunu tespit et
2. Ya da Claude Agent terminaline YAPISTIR (Ctrl+V) yap - kullaniciya metni
   kopyala ve kendisinin yapistirmasini iste
3. Veya: VS Code extension API'si uzerinden dogrudan terminal.sendText() cagir
   (ileri seviye, CLI ile)

Alternatif cozum: wscript.Shell SendKeys + AppActivate daha guvenilir olabilir

## Genel Hatalar ve Cozumleri

| Hata | Sebep | Cozum |
|------|-------|-------|
| "Chat bokumu aciliyor" | Yanlis koordinat -> normal VS Code chat butonuna tikliyor | Kullanicidan Claude Agent terminaline tiklamasini iste, yeni koordinat al |
| "Ekran tamami secildi" | ctrl+a kullanildi | ASLA ctrl+a kullanma - direkt pyautogui.write() |
| "iptal mi oldu" | Fare tiklamasi odagi kaydirdi | Script calisirken fareye dokunma - kullanici uyar |
| "Wi agi cin i nelerdir yazdin" | Harfler kayboldu/atladi | interval=0.05 yerine 0.1-0.15 kullan, yavas yaz |
| "Birden fazla yere yaziyor" | Koordinat yanlis veya VS Code odak kaydiriyor | Bkz: OTOM VS CODE ODAK SORUNU |

## Son Koordinat Gecmisi

| Tarih | Koordinat | Tur | Durum |
|-------|-----------|-----|-------|
| 03.06.2026 | (1282, 767) | Claude Agent | Calisti |
| 03.06.2026 | (978, 612) | Claude Agent | Calisti |
| 03.06.2026 | (967, 363) | Claude Agent | Calisti |
| 03.06.2026 | (774, 290) | Claude Agent | Calisti |
| 03.06.2026 | (619, 232) | Claude Agent | Calisti |
| 03.06.2026 | (1113, 166) | Claude Agent | CALISTI (son dogru) |
| 03.06.2026 | (890, 133) | Claude Agent | Hatali |
| 03.06.2026 | (606, 802) | Claude Agent | Hatali |
| 03.06.2026 | (646, 773) | Claude Agent | Hatali |
| 03.06.2026 | (1302, 277) | Normal Terminal | Saklandi |

## Iki Terminal Turu

1. Claude Agent Sohbet Terminali — Claude AI chat input kutusu
   - Yüksekte, ust panelde
   - Direkt soru/metin yaz + Enter gonder
   - Komut calistirmaz, Claude AI'ya mesaj gonderir

2. VS Code Normal Terminal — bash/PowerShell komut satiri
   - Altta, panelde
   - echo/ls/cd/python gibi shell komutlari calistirir
   - Komutlar echo "..." ile baslamali

Her kullanimda kullaniciya hangi terminale tiklayacagini net soyle, turu ayirt et.
