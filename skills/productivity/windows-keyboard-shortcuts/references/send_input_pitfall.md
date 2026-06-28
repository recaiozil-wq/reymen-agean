---
skill_id: ee5573517b7f
usage_count: 1
last_used: 2026-06-16
---
# Windows SendInput Pitfall

## Hata: TypeError: 'NoneType' object is not iterable
`SendInput` wrapper ile string gonderdigin zaman alinan hata.
**Sebep:** Wrapper fonksiyonu karakter dizisini doğru şekilde tüketemiyor.
**Önlem:** Eski yöntemi kullanma; `ctypes.windll.user32.keybd_event` ya da `PowerShell SendKeys` kullan.
**Referans:** Windows 10 uygulama yakalama (Alt+Tab) için `SendKeys` çözümü doğrulandı.